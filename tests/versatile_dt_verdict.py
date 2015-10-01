#!/usr/bin/env python

import verdict

def run():
	verdict.build('config versatile_defconfig ' +
		'--modernize --nfs --enable MACH_VERSATILE_DT')

	qemu = verdict.qemu('qemu-system-arm ' +
		'-M versatilepb -m 256M -nographic ' +
		'-serial tcp::5331,server ' +
		'-dtb arch/arm/boot/dts/versatile-pb.dtb ' +
		'-kernel arch/arm/boot/zImage ' +
		'-append "console=ttyAMA0,115200 kgdboc=ttyAMA0 ' +
		'rq nfsroot=10.0.2.2:/opt/debian/jessie-armel-rootfs,v3 ' +
		'ip=dhcp"')

	uart = verdict.telnet('localhost', 5331)
	verdict.expect_slow_replies(uart)
	verdict.expect_systemd_boot(uart, 'Uncompressing Linux...')

	verdict.good(cleanup=(uart, qemu))

if __name__ == "__main__":
	run()
