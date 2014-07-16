#!/usr/bin/env python

import sys, verdict

def run(args=[]):
	config = ['config multi_v7_defconfig --modernize']
	console = 'console=ttyAS0,115200'

	for arg in args:
		if arg.startswith('CONFIG_'):
			config.append('config --enable ' + arg)

	if 'thumb' in args:
		config.append('config --thumb')

	if 'fiq' in args:
		config.append('config --kgdb ' +
				'--enable KGDB_FIQ --enable SERIAL_KGDB_NMI')
		console = 'console=ttyNMI0 kgdboc=ttyAS0,115200 kgdb_fiq.enable=1'

	verdict.build(config)
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
		console + ' ' +
		'root=/dev/nfs rw ' +
		'nfsroot=192.168.1.33:/opt/debian/jessie-armel-rootfs,tcp,v3 ' +
'ip=192.168.1.39:192.168.1.33:192.168.1.1:255.255.255.0:curry:eth0:off ' +
		'ipconfdelay=0 clk_ignore_unused')

	verdict.expect_systemd_boot(uart)
	if 'fiq' in args:
		verdict.expect_nmi_debugger(uart)
	verdict.expect_login_prompt(uart)
	if 'fiq' in args:
		verdict.expect_nmi_debugger(uart)
		verdict.expect_nmi_debugger(uart)

	verdict.good((uart, gdb))

if __name__ == '__main__':
	run(sys.argv[1:])
