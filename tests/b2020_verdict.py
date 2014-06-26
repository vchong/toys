#!/usr/bin/env python

import verdict

def run():
	verdict.build('config multi_v7_defconfig --modernize')

	uart = verdict.telnet('agnes', 5331)
	gdb = verdict.stlinux_arm_boot('stlinux_arm_boot ' +
		'-t agnes:b2020stxh416:a9_0,' +
		        'no_convertor_abort=1,' +
			'stmc_core_param_stop_on_exception=0,' +
			'stmc_core_param_stop_on_svc=0,' +
			'stmc_core_param_coresight_debug_flags=0,' +
			'uart_setup=1 ' +
		'-L -dtb arch/arm/boot/dts/stih416-b2020.dtb ' +
		'-b vmlinux -- ' +
		'console=ttyAS0,115200 ' +
		'root=/dev/nfs rw ' +
		'nfsroot=192.168.1.33:/opt/debian/jessie-armel-rootfs,tcp,v3 ' +
'ip=192.168.1.39:192.168.1.33:192.168.1.1:255.255.255.0:curry:eth0:off ' +
		'ipconfdelay=0')

	verdict.expect_systemd_boot(uart)
	verdict.good((uart, gdb))

if __name__ == '__main__':
	run()
