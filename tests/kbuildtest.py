#!/usr/bin/env python3

#
# kbuildtest.py
#
# Automatically build test a wide range of ARM kernels.
#

#
# Usage:
#
#   <change into a mrproper'd kernel source directory>
#   nice ionice <path_to>/kbuildtest.py
#
# Interactive usage (single build):
#
#   <change into a mrproper'd kernel source directory>
#   PYTHONPATH=<path_to_kbuildtest.py> \
#   python -m unittest --verbose \
#       kbuildtest.TestArm64KernelBuilds.test_defconfig
#

#
# Note:
#   If you don't have python3 try in python2... it will probably just work
#

import os
import unittest

#
# Utility class
#

class KbuildSuite(unittest.TestCase):
    def setUpAndApplyConfig(self, arch, cross_compile, toolchain):
        os.environ['ARCH'] = arch

        if cross_compile:
            os.environ['CROSS_COMPILE'] = cross_compile
        else:
            if 'CROSS_COMPILE' in os.environ:
                del os.environ['CROSS_COMPILE']

        self.origpath = os.environ['PATH']
        if toolchain:
            os.environ['PATH'] = toolchain + '/bin:' + os.environ['PATH']

        testname = str(self).split()[0]
        self.board = testname[5:]
        self.objdir = '-'.join(('objdir', arch, self.board))

        if (not os.access(self.objdir, os.R_OK | os.W_OK | os.X_OK)):
            os.mkdir(self.objdir)

        config_rule = self.board
        if config_rule.startswith('defconfig_'):
            config_rule = 'defconfig'

        exit_code = os.system('make O=%s %s > %s/lastbuild.log 2>&1'
                % (self.objdir, config_rule, self.objdir))
        self.assertEqual(0, exit_code,
            'Initial config failed: See "%s/lastbuild.log"' % (self.objdir,))

        f = open(self.objdir + '/.gitignore', 'w')
        f.write('*\n')
        f.close()

    def tearDown(self):
        # Every single test impacts ARCH and CROSS_COMPILE so we will
        # leave them alone.
        os.environ['PATH'] = self.origpath

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
        if 'JOBS' in os.environ:
            jobs = os.environ['JOBS']
        else:
            jobs = os.sysconf('SC_NPROCESSORS_ONLN')
        exit_code = os.system('make -C %s -j %s %s >> %s/lastbuild.log 2>&1'
            % (self.objdir, jobs, cmd, self.objdir))
        self.assertEqual(0, exit_code,
            'Build failed: See "%s/lastbuild.log"' % (self.objdir))

#
# ARM
#

class TestArmKernelBuilds(KbuildSuite):
    def setUp(self):
        self.setUpAndApplyConfig('arm', 'arm-linux-gnueabihf-',
            '/opt/linaro/gcc-linaro-arm-linux-gnueabihf-4.8-2014.01_linux')

    def test_at91_dt_defconfig(self):
        self.make()

    def test_clps711x_defconfig(self):
        self.make()

    def test_ep93xx_defconfig(self):
        self.make()
        self.config(disable='DEBUG_LL')

    def test_footbridge_defconfig(self):
        self.make()

    def test_integrator_defconfig(self):
        self.make()

    def test_ixp4xx_defconfig(self): # big endian
        self.make()

    def test_ks8695_defconfig(self):
        self.make()

    def test_multi_v7_defconfig(self):
        self.make()
        self.config_modernize()
        self.config_kgdb()
        self.make()

    def test_netx_defconfig(self):
        self.make()

    def test_omap1_defconfig(self):
        self.make()

    def test_lart_defconfig(self): # ARCH_SA1100
        self.make()

    def test_spear6xx_defconfig(self):
        self.make()

    def test_spear13xx_defconfig(self):
        self.make()

    def test_s3c2410_defconfig(self):
        self.make()

    def test_s5pv210_defconfig(self):
        self.make()

    def test_versatile_defconfig(self):
        self.make()
        self.config(disable='DEBUG_LL')
        self.config_modernize()
        self.config_kgdb()

#
# ARM64
#

class TestArm64KernelBuilds(KbuildSuite):
    def setUp(self):
        self.setUpAndApplyConfig('arm64', 'aarch64-linux-gnu-',
            '/opt/linaro/gcc-linaro-aarch64-linux-gnu-4.8-2014.04_linux')

    def test_defconfig(self):
        self.make()

    def test_defconfig_kgdb(self):
        self.config_kgdb()
        self.make()

    def xtest_allyesconfig(self):
        self.make()

    def xtest_allmodconfig(self):
        self.make()

#
# m68k
#

class TestM68kKernelBuilds(KbuildSuite):
    def setUp(self):
        self.setUpAndApplyConfig('m68k', 'm68k-linux-',
            '/opt/crosstool/gcc-4.9.0-nolibc/m68k-linux')

    def test_defconfig(self):
        self.make()

    def test_allmodconfig(self):
        self.make()

#
# PowerPC
#

class TestPowerpcKernelBuilds(KbuildSuite):
    def setUp(self):
        self.setUpAndApplyConfig('powerpc', 'powerpc64-linux-',
                '/opt/crosstool/gcc-4.8.0-nolibc/powerpc64-linux')

    def test_defconfig(self):
        self.make()

    def test_defconfig_kgdb(self):
        self.config_kgdb()
        self.make()

#
# X86
#

class TestX86KernelBuilds(KbuildSuite):
    def setUp(self):
        self.setUpAndApplyConfig('x86', None, None)

    def test_defconfig(self):
        self.make()
        self.config(disable='NFSD')
        self.config(enable='NFSD')
        self.config(enable='NFSD_V4')
        self.config(enable='NFSD_PNFS')
        self.config(enable='NFSD_V3')
        self.config(disable='NFSD_V4')

    def test_defconfig_kgdb(self):
        self.config_kgdb()
        self.make()

    def test_allyesconfig(self):
        self.make()

    def test_allmodconfig(self):
        self.make()

#
# Basic test runner
#

if __name__ == '__main__':
    unittest.main()
