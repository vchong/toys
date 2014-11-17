#!/usr/bin/env python

#
# vexpress_android_verdict.py
#

from __future__ import print_function

import verdict

def run():
	verdict.build('config multi_v7_defconfig --modernize --nfs --nls --android')
	qemu = verdict.qemu('qemu-system-arm ' +
		' -M vexpress-a9 -cpu cortex-a9 -m 1G ' +
		'-nographic -vnc :0 --no-reboot ' +
		'-serial tcp::5331,server ' +
		'-kernel arch/arm/boot/zImage ' +
		'-dtb arch/arm/boot/dts/vexpress-v2p-ca9.dtb ' +
		'-initrd /sandpit/sundance/drt/linaro-14.09-android-vexpress-lsk-3.14/initrd -sd /sandpit/sundance/drt/linaro-14.09-android-vexpress-lsk-3.14/vexpress.img ' +
		'-append "console=tty0 console=ttyAMA0,38400n8 rootwait rw init=/init androidboot.console=ttyAMA0 androidboot.selinux=disabled"')
	uart = verdict.telnet('localhost', 5331)
	verdict.expect_slow_replies(uart)
	verdict.expect_kernel_boot(uart)

	# Try to get logcat running
	try:
		uart.expect('root@vexpress')
		uart.timeout = uart.timeout / 4
		#uart.send("logcat | grep -v '^D'\r")
		uart.send("logcat\r")
		# --------- beginning of /dev/log/main
		uart.expect('beginning of ')
	except:
		verdict.bad('logcat is not receiving trace')

	# We need to see each of these items at least once to call the
	# boot successful

	patterns = [
	### SPECIFIC MESSAGES
	# I/DEBUG   (   70): debuggerd: Sep 21 2014 17:25:45
		'\nI/DEBUG.*debuggerd',
	# I/SurfaceFlinger(   71): SurfaceFlinger is starting
		'\nI/SurfaceFlinger.*SurfaceFlinger is starting',
	# I/SurfaceFlinger(   70): Boot is finished (343035 ms)
		'\nI/SurfaceFlinger.*Boot is finished',
	# I/AudioFlinger(   74): Using default 3000 mSec as standby time.
		'\nI/AudioFlinger.*Using .* as standby time',
	# I/PowerManagerService(  761): Going to sleep due to screen timeout...
		'\nI/PowerManagerService.*Going to sleep due to screen timeout',

	### PROCESSES
		'\n[DVIWE]/ActivityManager',
		'\n[DVIWE]/AndroidRuntime',
		'\n[DVIWE]/ARMAssembler',
		'\n[DVIWE]/dalvikvm',
		'\n[DVIWE]/gralloc',
		'\n[DVIWE]/healthd',
		'\n[DVIWE]/SurfaceFlinger',
		'\n[DVIWE]/libEGL',
		'\n[DVIWE]/LibraryLoader',
		'\n[DVIWE]/System',
		'\n[DVIWE]/SystemServer',
		'\n[DVIWE]/PackageManager',
		'\n[DVIWE]/WindowManager',
		'\n[DVIWE]/Zygote',

	# Ensure we capture all the logs...
		#'\nTHIS NEEDLE WILL NEVER BE FOUND. <evil-laugh\>'
	]
	counts = [ 0 for dummy in patterns ]

	# Loop until each pattern has been matched at least once
	try:
		while reduce(lambda x, y: x or (y == 0), counts, False):
			counts[uart.expect(patterns)] += 1
			if sum(counts) > 1500:
				raise Exception('Too many logcat messages')
	except:
		print("### PATTERN COUNT SUMMARIES ###")
		for (p, c) in zip(patterns, counts):
			print("%-4s%4d: %s" % ('' if c else '>>>', c, p.strip()))
		print('### Matched %d messages' % (sum(counts),))
		print('### END ###')
		verdict.bad('logcat did not output all expected patterns')

	print('### Matched %d messages' % (sum(counts),))
	verdict.good((uart, qemu))

if __name__ == '__main__':
	run()
