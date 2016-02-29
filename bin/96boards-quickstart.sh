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
	mosh tmux rsync \
	make \
	man-db \
	vim-nox

mkdir -p ~/Projects

pushd ~/Projects
git clone https://github.com/daniel-thompson/toys.git
cd toys
make
mv ~/public ~/Apps
popd

