#!/usr/bin/env python

import sys, verdict

def run(args=[]):
	verdict.build('config versatile_defconfig --modernize --nfs')
	console = 'console=ttyAMA0,115200 kgdboc=ttyAMA0'

	if 'fiq' in args:
		verdict.build('config --kgdb --enable PRINTK_TIME ' +
				'--enable KGDB_FIQ --enable SERIAL_KGDB_NMI')
		console = 'console=ttyNMI0 kgdboc=ttyAMA0,115200 kgdb_fiq.enable=1'

	qemu = verdict.qemu('qemu-system-arm ' + 
		'-M versatilepb -m 256M -nographic ' +
		'-serial tcp::5331,server ' +
		'-kernel arch/arm/boot/zImage ' +
		'-append "' + console + ' '+
		'rw nfsroot=10.0.2.2:/opt/debian/jessie-armel-rootfs,v3 ' +
		'ip=dhcp"')

	uart = verdict.telnet('localhost', 5331)

	verdict.expect_slow_replies(uart)
	verdict.expect_systemd_boot(uart, 'Uncompressing Linux...')
	if 'fiq' in args:
		verdict.expect_nmi_debugger(uart)
	verdict.expect_login_prompt(uart)
	#if 'fiq' in args:
	#	verdict.expect_nmi_debugger(uart)
	#	verdict.expect_nmi_debugger(uart)

	verdict.good((uart, qemu))

if __name__ == '__main__':
	run(sys.argv[1:])
