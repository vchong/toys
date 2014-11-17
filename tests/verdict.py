#!/usr/bin/env python

#
# verdict.py
#
# Library functions for runtime verdict generation
#

from __future__ import print_function

import os
import pexpect
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

def good(msg, cleanup=()):
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

def build(cmds=()):
	try:
		for cmd in destringize(cmds):
			run(cmd)

		# Avoid collisions in /lib/modules by setting the local version
		# to our username.
		run('scripts/config --set-str LOCALVERSION -$USER-')
		run('make CC="ccache %sgcc" -j 24' % (os.environ['CROSS_COMPILE'],))
		run('make INSTALL_MOD_PATH=/opt/debian/jessie-armel-rootfs modules_install')
	except:
		skip("Cannot compile")

def telnet(host, port=23, logfile=sys.stdout):
	"""Connect to telnet socket with automatic failure reporting."""
	try:
		s = pexpect.spawn('telnet %s %d' % (host, port), logfile=logfile)
		s.expect('Connected to ')
		s.expect('Escape character is')
		return s
	except:
		bad("Cannot aaccess %s:%s" % (host, port))

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
		print("qemu is waiting for connection")
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
	s.expect('debian-[^ ]* login:')

