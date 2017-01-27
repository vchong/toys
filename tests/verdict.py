#!/usr/bin/env python

#
# verdict.py
#
# Library functions for runtime verdict generation
#

from __future__ import print_function

import os
import pexpect
import pexpect.fdpexpect
import time
import traceback
import sys

def run(cmd):
	"""Run a command (synchronously) raising an exception on
	failure.

	"""
	print(cmd)
	(exit_code) = os.system(cmd)
	if exit_code != 0:
		raise Exception

def skip(msg):
	"""Exception handler with return code causing bisect to skip."""
	traceback.print_exc()
	print('### SKIP: %s ###' % (msg,))
	sys.exit(125) # skip

def bad(msg):
	"""Exception handler causing bisect to mark revision bad."""
	traceback.print_exc()
	print('### BAD: %s ###' % (msg,))
	sys.exit(1)

def good(cleanup=()):
	"""Report success and exit."""
	for f in cleanup:
		f.close()
	print('\n### GOOD: Observed boot messages ###')

def warn(msg):
	"""Report a warning (and continue)."""
	print('\n### WARNING: %s ###' % (msg,))

def destringize(s):
	if isinstance(s, basestring):
		return (s,)
	return s

def build(cmds=(), modules=True):
	try:
		for cmd in destringize(cmds):
			run(cmd)

		# Avoid collisions in /lib/modules by setting the local version
		# to our username.
		run('scripts/config --set-str LOCALVERSION -$USER-')
		run('make CC="ccache %sgcc" -j 24' % (os.environ['CROSS_COMPILE'],))
		if modules:
			run('make INSTALL_MOD_PATH=/opt/debian/jessie-armel-rootfs modules_install')
	except:
		skip("Cannot compile")

def serial(port, baud=115200, logfile=sys.stdout):
	"""Connect to serial port with automatic failure reporting."""
	try:
		return pexpect.spawn('socat - %s,raw,echo=0,ispeed=%d,ospeed=%d' % (port, baud, baud), logfile=logfile)
	except:
		bad("Cannot open %s" % (port,))

def telnet(host, port=23, logfile=sys.stdout):
	"""Connect to telnet socket with automatic failure reporting."""
	try:
		s = pexpect.spawn('telnet %s %d' % (host, port), logfile=logfile)
		s.expect('Connected to ')
		s.expect('Escape character is')
		return s
	except:
		bad("Cannot access %s:%s" % (host, port))

def netcat(host, port, logfile=sys.stdout):
	"""Connect to a raw socket with automatic failure reporting."""
	try:
		return pexpect.spawn('nc %s %d' % (host, port), logfile=logfile)
	except:
		bad("Cannot access %s:%s" % (host, port))

def fvp(logfile=sys.stdout):
	"""Launch fvp and wait for sockets to open, without automatic
	failure reporting.
	"""

	FVP = '/home/drt/Apps/Foundation_Platformpkg'
	FIRMWARE = '/home/drt/Development/Linaro/ARM/16.06/binaries'
	BUILDROOT = '/home/drt/Development/Buildroot/buildroot-aarch64'

	try:
		cmd = ('{}/models/Linux64_GCC-4.1/Foundation_Platform ' +
			'--cores=4 ' +
			'--no-secure-memory ' +
			'--visualization ' +
			'--gicv3 ' +
			'--data={}/bl1.bin@0x0 ' +
			'--data={}/fip.bin@0x8000000 ' +
			'--data=arch/arm64/boot/Image@0x80080000 ' +
			'--data=arch/arm64/boot/dts/arm/fvp-foundation-gicv3-psci.dtb@0x83000000 ' +
			'--data={}/ramdisk.img@0x84000000 ' +
			'--block-device={}/output/images/rootfs.ext2'
		      ).format(FVP, FIRMWARE, FIRMWARE, FIRMWARE, BUILDROOT)

		print(cmd)
		fvp = pexpect.spawn(cmd, logfile=logfile)

		fvp.expect('Listening for serial connection on port ([0-9]+)')
                port = int(fvp.match.group(1))
		fvp.expect('Simulation is started')
		print("Simulation is started")

		uart = telnet('localhost', port)

		return (fvp, uart)
	except:
		bad("Cannot boot")

def qemu(cmd, logfile=None):
	"""Launch qemu and wait for sockets to open, with automatic
	failure reporting.

	This command assumes cmd includes a -serial tcp::XXX,server
	argument.

	"""
	try:
		print(cmd)
		q = pexpect.spawn(cmd, logfile=logfile)

		q.expect('QEMU waiting for connection')
                print("QEMU waiting for connection")

		return q
	except:
		bad("Cannot boot")

def stlinux_arm_boot(cmd, logfile=None):
	"""Launch stlinux_arm_boot and wait for the kernel to start booting."""

	def boot(cmd):
		print(cmd)
		g = pexpect.spawn(cmd, logfile=logfile)
		g.expect('Kernel auto-detected')
		g.expect('Booting')
		# TODO: recognise SDI.*ERROR and bail out without the timeout
		g.expect('Switching to Thread')
		g.expect('Loading section')

	try:
		boot(cmd)
	except:
		warn('cannot connect, retrying')
		try:
			# Kill it nicely
			run('killall armv7-linux-unw')
			time.sleep(5)

			# Kill it nastily (this will fail if nice worked...)
			try:
				run('killall -KILL armv7-linux-unw')
				time.sleep(5)
			except:
				pass

			# Retry
			boot(cmd)
		except:
			bad("Cannot boot")

def cmd(s, cmd):
	s.sendline(cmd)
	s.expect('root.*# ')
	s.sendline('echo $?')
	s.expect('0')
	s.expect('root.*# ')

def expect_slow_replies(s):
	s.timeout *= 4

def expect_kernel_boot(s, bootloader=()):
	try:
		for msg in destringize(bootloader):
			s.expect(msg)
		s.expect('Booting Linux') # 0.000000
		s.expect('Kernel command line.*$')
		s.expect('Calibrating delay loop...')
		s.expect('NET: Registered protocol family 2')
		s.expect('io scheduler [^ ]* registered .default.')
		s.expect('Freeing unused kernel memory')
	except:
		bad('Incorrect boot activity messages (kernel)')

def expect_buildroot_boot(s, bootloader=()):
	"""Observe a typical boot sequence until we see evidence of
	buildroot init issuing messages to the console.

	"""
	expect_kernel_boot(s, bootloader);

	try:
		s.expect('Starting logging')
                s.expect('OK')
                s.expect('Welcome to Buildroot')
	except:
		bad('Incorrect boot activity messages (buildroot)')

def expect_systemd_boot(s, bootloader=()):
	"""Observe a typical boot sequence until we see evidence of
	systemd issuing messages to the console.

	"""
	expect_kernel_boot(s, bootloader);

	try:
		s.expect('Listening on Syslog Socket.')
	except:
		bad('Incorrect boot activity messages (systemd)')

def expect_nmi_debugger(s):
	"""Interact with the NMI debugger"""
	try:
		s.send('\r')

		# This tries to defeat character interleaving as boot messages
		# interact with the FIQ messages (although it won't work
		# perfectly). Without interleaving we could have something like:
		# s.expect('Type [^ ]* to enter the debugger')
		s.expect('[$][^3]*[3][^#]*#[^3]*3[^3]*3')

		s.send('$3#33\r')
		s.expect('Entering kdb .* due to NonMaskable Interrupt')
		s.expect('more>')
		s.send('q\r')
		s.expect('kdb>')
		s.send('go\r')
	except:
		bad('Cannot interact with NMI debugger')

def expect_login_prompt(s):
	"""Wait for the login prompt"""
	s.expect(['debian-[^ ]* login:', 'buildroot login:'])

