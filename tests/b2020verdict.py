#!/usr/bin/env python

#
# b2020verdict.py
#

from __future__ import print_function

import os
import pexpect
import sys

def run(cmd):
	print(cmd)
	(exit_code) = os.system(cmd)
	if exit_code != 0:
		raise Exception

#
# Build
#

try:
	#run('make multi_v7_defconfig')
	run('config multi_v7_defconfig --disable ARCH_BCM --disable ORION_WATCHDOG --disable ARCH_SOCFPGA')
	run('make -j24')
except:
	print('### SKIP: Cannot compile ###')
	sys.exit(125) # skip

#
# Setup
#

uart = pexpect.spawn('telnet agnes.lan 5331', logfile=sys.stdout)
uart.expect('Connected to ')
uart.expect('Escape character is')

#
# Boot
#

try:
	run('stlinux_arm_boot -L -r -t agnes:b2020stxh416:a9_0,no_convertor_abort=1,stmc_core_param_stop_on_exception=0,stmc_core_param_stop_on_svc=0,stmc_core_param_coresight_debug_flags=0,uart_setup=1 -dtb arch/arm/boot/dts/stih416-b2020.dtb -b vmlinux -- console=ttyAS0,115200 kgdboc=ttyAS0 root=/dev/nfs rw nfsroot=192.168.1.33:/opt/debian/wheezy-armhf-rootfs,tcp,v3 ip=192.168.1.39:192.168.1.33:192.168.1.1:255.255.255.0:curry:eth0:off ipconfdelay=0')
except:
	print('### BAD: Cannot boot ###')
	sys.exit(1)

#
# Verdict
#

try:
	uart.expect('This UART ([^ ]*) is preconfigured from targetpack')
	uart.expect('Booting Linux') # 0.000000
	uart.expect('Kernel command line.*$')
except:
	print('### BAD: No UART activity ###')
	sys.exit(2)

#
# Tear down and exit
#

uart.close()
print('\n### GOOD: Observed boot messages ###')
sys.exit(0)

	
