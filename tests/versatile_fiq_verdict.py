#!/usr/bin/env python

#
# versatile_fiq_verdict.py
#

import verdict

def run():
	verdict.build('config versatile_defconfig ' +
		'--kgdb --nfs --modernize ' +
		'--enable PRINTK_TIME ' +
		'--enable KGDB_FIQ --enable SERIAL_KGDB_NMI')
	qemu = verdict.qemu('qemu-system-arm ' + 
		'-M versatilepb -m 256M -nographic ' +
		'-serial tcp::5331,server ' +
		'-kernel arch/arm/boot/zImage ' +
		'-append "console=ttyNMI0 kgdboc=ttyAMA0,115200 kgdb_fiq.enable=1 ' +
		'rw nfsroot=10.0.2.2:/opt/debian/jessie-armel-rootfs,v3 ' +
		'ip=dhcp"')
	uart = verdict.telnet('localhost', 5331)
	verdict.expect_slow_replies(uart)
	verdict.expect_systemd_boot(uart, 'Uncompressing Linux...')

	# Interact with the NMI debugger
	uart.send('\r')
	uart.expect('Type [^ ]* to enter the debugger')
	uart.send('$3#33\r')
	uart.expect('Entering kdb .* due to NonMaskable Interrupt')
	uart.expect('more>')
	uart.send('q\r')
	uart.expect('kdb>')
	uart.send('go\r')
	uart.expect('debian-[^ ]* login:')

	verdict.good(cleanup=(uart, qemu))

if __name__ == '__main__':
	run()
