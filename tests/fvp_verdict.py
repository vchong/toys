#!/usr/bin/env python

import os, sys, verdict

def run(args=[]):
	os.putenv('XTERM_IS_NOP', 'y') 

	verdict.build((
		'config defconfig ' +
                        '--kgdb --nfs --modernize --pedantic ' +
			'--enable DEBUG_SPINLOCK ' +
			'--enable PROVE_LOCKING ' +
			'--enable USE_ICC_SYSREGS_FOR_IRQFLAGS ' +
			'--enable MAGIC_SYSRQ_BREAK_EMULATION ' +
			'--enable CMDLINE_FORCE ',
		'scripts/config --set-str CMDLINE ' +
			'"console=ttyAMA0,115200 root=/dev/vda efi=noruntime"'
		), modules=False)

	(fvp, uart) = verdict.fvp()

	verdict.expect_slow_replies(uart)
	verdict.expect_buildroot_boot(uart, 'U-Boot')
	verdict.expect_login_prompt(uart)

	# login and set the prompt to match what verdict.cmd expects
	uart.sendline('root')
	uart.expect('# ')
	uart.sendline('PS1=root@busybox#\\ ')
	uart.expect('root.*# ')

	verdict.cmd(uart, 'stress-ng --cpu 8 --io 4 --vm 2 --vm-bytes 128M ' +
				'--fork 4 --timeout 10s')
	
	# TODO: Run a quick stress-ng test

	verdict.good(cleanup=(uart, fvp))

if __name__ == '__main__':
	run(sys.argv[1:])
