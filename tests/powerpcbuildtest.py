#!/usr/bin/env python3

#
# powerpcbuildtest.py
#
# Automatically build test a wide range of ARM kernels.
#

#
# Usage:
#   <change into a mrproper'd kernel source directory>
#   ARCH=powerpc CROSS_COMPILE=powerpc64-linux- \
#       nice ionice <path_to>/powerpcbuildtest.py
#
# Note:
#   If you don't have python3 try in python2... it will probably just work
#

import os
import unittest

class TestPowerpcKernelBuilds(unittest.TestCase):
    def setUp(self):
        testname = str(self).split()[0]
        self.board = testname[5:]
        self.objdir = 'objdir-powerpc-' + self.board

        if (not os.access(self.objdir, os.R_OK | os.W_OK | os.X_OK)):
            os.mkdir(self.objdir)

        config_rule = self.board
        if config_rule.startswith('defconfig_'):
            config_rule = 'defconfig'

        exit_code = os.system('make O=%s %s > %s/lastbuild.log 2>&1'
                % (self.objdir, config_rule, self.objdir))
        self.assertEqual(0, exit_code,
            'Initial config failed: See "%s/lastbuild.log"' % (self.objdir,))

    def tearDown(self):
        pass

    def config(self, enable=(), disable=(), module=()):
        if isinstance(enable, str):
            enable = (enable,)
        enable = ' '.join([ '--enable ' + x for x in enable ])

        if isinstance(disable, str):
            disable = (disable,)
        disable = ' '.join([ '--disable ' + x for x in disable ])

        if isinstance(module, str):
            module = (module,)
        module = ' '.join([ '--module ' + x for x in module ])

        exit_code = os.system(
            'scripts/config --file %s/.config %s %s %s >> %s/lastbuild.log 2>&1'
                % (self.objdir, enable, module, disable, self.objdir))
        self.assertEqual(0, exit_code, 
            'Config failed: See "%s/lastbuild.log"' % (self.objdir,))

        exit_code = os.system('make -C %s olddefconfig > %s/lastbuild.log 2>&1'
                % (self.objdir, self.objdir))
        self.assertEqual(0, exit_code,
            'olddefconfig failed: See "%s/lastbuild.log"' % (self.objdir,))

        self.make()

    def config_modernize(self):
        # Ensure the kernel can support:
        #   recent udev
        #   systemd
        #   NFS root (with DHCP)
        self.config(enable=('TMPFS', 'DEVTMPFS', 'CGROUPS',
                            'IP_PNP', 'IP_PNP_DHCP'),
                    module=('AUTOFS4_FS', 'IPV6'))

    def config_kgdb(self):
        # This deliberately omits DEBUG_INFO to keep the build size down...
        self.config(('MAGIC_SYSRQ', 'MAGIC_SYSRQ_BREAK_EMULATION',
                     'KGDB', 'KGDB_KDB'))

    def make(self, cmd=''):
        exit_code = os.system('make -C %s -j 24 %s >> %s/lastbuild.log 2>&1' 
            % (self.objdir, cmd, self.objdir))
        self.assertEqual(0, exit_code,
            'Build failed: See "%s/lastbuild.log"' % (self.objdir))

    def test_defconfig(self):
        self.make()

    def test_defconfig_kgdb(self):
        self.config_kgdb()
        self.make()

if __name__ == '__main__': unittest.main()
