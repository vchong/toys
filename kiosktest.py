#!/usr/bin/env python3

#
# kiosktest.py
#
# Automatically deployable tests to run a quick test on kdb's kiosk
# feature.
#

import unittest
import pexpect	   # Needs to be pexpect >= 3.1
import pxssh
import time
import sys

UARTCMD='telnet agnes.lan 5331'
TARGETIP='192.168.1.39'

class TestKdbKiosk(unittest.TestCase):
	"""A collection of tests for kdb's kiosk mode.

	This suite is based on two pexpect sessions. One, the uart, is 
	pointed at the serial port and is used to interact with kdb, 
	the other, the manager, is pointed at an SSH session on the 
	system-under-test (target).

	The SSH session is used to change sysfs settings, to make other
	administrative changes to the target and to trigger entry into
	the debugger. The UART session is used for everything else.
	
	"""

	@classmethod
	def setUpClass(cls):
		"""Open network connections that can be reused.

		This optimization is important because it saves us about
		two seconds per test meaning we can write smaller and more
		focused test cases without a sprawling execution time.

		"""
		#cls.uart = pexpect.spawn('target-jei-serial agnes.lan')
		cls.uart = pexpect.spawn(UARTCMD)
		cls.uart.expect('Connected to ')
		cls.uart.expect('Escape character is')
		# Make absolutely sure the target is running (otherwise
		# SSH interaction will fail)
		cls.uart.send('q\r') # break out of the pager
		cls.uart.send('go\r') # set the target running

		cls.mgr = pxssh.pxssh()
		cls.mgr.login(TARGETIP, 'root')

	@classmethod
	def tearDownClass(cls):
		cls = cls
		cls.uart.close()
		cls.mgr.close()

	def setUp(self):
		# Automatically select the right kdb operating mode
		testname = str(self).split()[0]
		kioskmode = 'kiosk' in testname.lower()
		self.setKioskMode(kioskmode)

		# Stop the target
		self.triggerInterrupt()

	def tearDown(self):
		# Make absolutely sure the target is running before we
		# manipulate the target via SSH
		self.sendCommand('q') # break out of the pager
		self.sendCommand('go') # set the target running

	def sendInterrupt(self):
		"""Interrupt the target using the UART.
		
		This can be tough to get running with some telnet proxies
		so this currently relies on an out-of-tree kernel patch to
		change the way SysRq works on serial consoles.

		"""
		def ctrl(c):
			return chr((ord(c) - ord('A'))+1)
		
		self.uart.send(ctrl('B') + ctrl('R') + ctrl('K') + 'g')
		self.uart.expect('kdb> ')

	def triggerInterrupt(self):
		self.mgr.sendline('echo g > /proc/sysrq-trigger')
		self.uart.expect('kdb> ')

	def prompt(self):
		self.uart.expect('kdb> ')

	def sendCommand(self, cmd, reply=None):
		self.uart.send(cmd + '\r')

		if reply:
			self.uart.expect(reply)

	def setKioskMode(self, mode):
		if mode:
			cmd = 'echo 1'
		else:
			cmd = 'echo 0'

		cmd += ' > /sys/module/kdb/parameters/kiosk'
		self.mgr.sendline(cmd)
		self.mgr.prompt()

	def testSendInterrupt(self):
		"""Check we can halt the target using the UART."""
		self.sendCommand('go')
		self.mgr.sendline('echo 1 > /proc/sys/kernel/sysrq')
		self.mgr.prompt()
		self.sendInterrupt()
		self.sendCommand('go')
		self.sendInterrupt()

	def testHelp(self):
		self.sendCommand('help')
		i = self.uart.expect(['Display Memory Contents',
		                      'Continue Execution'])
		self.assertEqual(i, 0)
		self.uart.expect('Modify Memory Contents')   # Unsafe
		self.uart.expect('Continue Execution')       # Safe
		self.uart.expect('Display exception frame')  # UnSafe
		self.uart.expect('more> ')
		self.uart.send('q')

	def testKioskHelp(self):
		#self.uart.logfile = sys.stdout
		self.sendCommand('help')
		i = self.uart.expect(['Display Memory Contents',
		                      'Continue Execution'])
		self.assertEqual(i, 1)
		self.uart.expect('Switch to new cpu')  # Safe
		self.uart.expect('more> ')
		self.uart.send(' ')
		self.uart.expect("Common kdb debugging")  # Safe (near end)
	
	def testKioskDisplayExceptionFrame(self):
		self.sendCommand('ef 0xDEDE', 'denied')
		self.prompt()

	def testSysRq(self):
		self.sendCommand('sr h', 'SysRq : HELP :')
		self.prompt()
		self.sendCommand('sr 4', 'SysRq : Changing Loglevel')
		self.prompt()

		# Check that the debugger can overcome the sysrq mask.
		#
		# This part is slightly complicated because when we have
		# disabled sysrq then we cannot use sysrq to enter the
		# debugger.
		self.sendCommand('go')
		self.mgr.sendline('echo 0 > /proc/sys/kernel/sysrq')
		self.mgr.prompt()
		self.triggerInterrupt()
		self.sendCommand('sr 4', 'SysRq : Changing Loglevel')
		self.prompt()
		self.sendCommand('go')
		self.mgr.prompt()
		self.mgr.sendline('echo 1 > /proc/sys/kernel/sysrq')
		self.mgr.prompt()
		


	def testKioskSysRq(self):
		self.sendCommand('sr h', 'SysRq : HELP :')
		self.prompt()
		self.sendCommand('sr 4', 'SysRq : Changing Loglevel')
		self.prompt()


		# Check that in kiosk mode the debugger cannot overcome
		# the sysrq mask.
		#
		# This part is slightly complicated because when we have
		# disabled sysrq then we cannot use sysrq to enter the
		# debugger.
		self.sendCommand('go')
		self.mgr.sendline('echo 0 > /proc/sys/kernel/sysrq')
		self.mgr.prompt()
		self.triggerInterrupt()
		self.sendCommand('sr 4', 'This sysrq operation is disabled')
		self.prompt()
		self.sendCommand('go')
		self.mgr.prompt()
		self.mgr.sendline('echo 1 > /proc/sys/kernel/sysrq')
		self.mgr.prompt()
		

if __name__ == '__main__':
	unittest.main()
