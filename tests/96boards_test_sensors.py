#!/usr/bin/env python

import sys, time, verdict

UART0 = '/dev/ttyMSM1'

def run(args=[]):
	#console = verdict.netcat('hazel', 5002)
	console = verdict.serial('/dev/ttyUSB0')

	# Check we have a command prompt
	console.sendline('')
	console.expect('root.*# ')

	# The next set of commands are network based commands and might 
	# have unpredictable runtimes
	verdict.expect_slow_replies(console)

	console.sendline('apt-get update')
	console.expect('Reading package lists')
	console.expect('root.*# ')

	console.sendline('apt-get install -y arduino arduino-mk make i2c-tools git')
	console.expect('Reading package lists')
	#console.expect('Unpacking arduino')
	#console.expect('Setting up arduino')
	console.expect('root.*# ')
	# TODO: write verdict.expect_apt_get_ok

	verdict.cmd(console, 'cd')
	verdict.cmd(console, 'mkdir -p sketchbook/Blink')
	verdict.cmd(console, 'cd sketchbook/Blink')
	verdict.cmd(console, 'cp /usr/share/arduino/examples/01.Basics/Blink/Blink.ino .')
	verdict.cmd(console, '''cat > Makefile << EOF
BOARD_TAG = uno
MONITOR_PORT = %s
include /usr/share/arduino/Arduino.mk
EOF''' % (UART0,))
	verdict.cmd(console, 'make')
	verdict.cmd(console, 'make upload')
	verdict.cmd(console, 'stty -F %s -hupcl' % (UART0,))
	verdict.cmd(console, 'cd')
	
	verdict.good(cleanup=(console,))

if __name__ == '__main__':
        run(sys.argv[1:])
