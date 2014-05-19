#!/bin/bash

#
# buildtest.sh
#
# Wrap all the XXXbuildtest.py scripts together.
#

# TODO: This script is a dumb idea (but it was quick to write). All the
#       build tests should be combined into a single python script.

libpath-prepend () {
	if [ -z "$LD_LIBRARY_PATH" ]
	then
		LD_LIBRARY_PATH=$1
	else
		echo $LD_LIBRARY_PATH | grep "$1" > /dev/null || \
			LD_LIBRARY_PATH=$1:$LD_LIBRARY_PATH
	fi
	export LD_LIBRARY_PATH
}

manpath-prepend () {
	echo $MANPATH | grep "$1" > /dev/null || \
		MANPATH=$1:$MANPATH
	export MANPATH
}

path-prepend () {
	echo $PATH | grep "$1" > /dev/null || \
		PATH=$1:$PATH
	export PATH
}

all-path-prepend () {
	libpath-prepend $1/lib
	libpath-prepend $1/lib64
	manpath-prepend $1/man
	path-prepend $1/bin
}

all-path-prepend /opt/linaro/gcc-linaro-arm-linux-gnueabihf-4.8-2014.01_linux
all-path-prepend /opt/crosstool/gcc-4.6.3-nolibc/hppa-linux
all-path-prepend /opt/crosstool/gcc-4.8.0-nolibc/powerpc64-linux

unset ARCH
unset CROSS_COMPILE
export ARCH CROSS_COMPILE

testdir=`dirname $0`

ARCH=x86 $testdir/x86buildtest.py --verbose
ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- $testdir/armbuildtest.py --verbose
ARCH=powerpc CROSS_COMPILE=powerpc64-linux- \
    $testdir/powerpcbuildtest.py --verbose

