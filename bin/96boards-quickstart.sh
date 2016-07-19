#!/bin/sh

#
# 96boards-quickstart.sh
#
[ "Usage" = "Copy the following five lines into your shell" ] && \
read -p "SSID: " ssid && read -sp "Password: " password && \
nmcli dev wifi connect "$ssid" password "$password" && \
repo=https://git.linaro.org/people/daniel.thompson/toys.git && \
wget $repo/blob_plain/HEAD:/bin/96boards-quickstart.sh && \
bash -x 96boards-quickstart.sh

# This is only temporary...
setxkbmap gb

# Set some passwords
echo "Need a new password for root user..."
sudo passwd root
echo "Need a new password for 'linaro' user..."
passwd

# Allow root SSH login (useful for make modules_install via sshfs)
sudo sed -ie 's/PermitRootLogin without-password/PermitRootLogin yes/' \
	/etc/ssh/sshd_config
sudo systemctl reload sshd

sudo apt-get update
sudo apt-get -y install \
	automake libtool build-essential fakeroot devscripts debhelper \
	patchelf \
	mosh tmux rsync \
	perl-base \
	make \
	man-db \
	vim-nox \
	arduino-mk arduino git swig3.0 python-dev nodejs-dev \
	cmake pkg-config libpcre3-dev \
	libfdt-dev

mkdir -p ~/Projects/upstream

pushd ~/Projects
git clone https://github.com/daniel-thompson/toys.git
cd toys
make
mv ~/public ~/Apps
popd

# This is only really useful on a db410c but I've been too lazy to
# figure out how to determine the machine type on arm64...
pushd ~/Projects/upstream
git clone git://codeaurora.org/quic/kernel/skales
popd
echo 'path-append $HOME/Projects/upstream/skales' > $HOME/.bashrc.d/skales.sh
