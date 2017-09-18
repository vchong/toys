#!/bin/sh

#
# 96boards-quickstart.sh
#
[ Usage = "Copy the five lines below (excluding this one) to your shell" ] && \
read -p "SSID: " ssid && read -sp "Password: " password && \
nmcli dev wifi connect "$ssid" password "$password" && \
repo=https://git.linaro.org/people/victor.chong/toys.git && \
wget $repo/plain/bin/96boards-quickstart.sh && \
bash -x 96boards-quickstart.sh

if [ "root" = "$USER" ]
then
	chmod a+rx /root
	exec su linaro -c "bash -x $0"
fi

# This is only temporary...
setxkbmap gb

# Set some passwords
echo "Need a new password for root user..."
sudo passwd root
echo "Need a new password for 'linaro' user..."
sudo passwd linaro

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
	libfdt-dev \
	locales

sudo locale-gen en_GB.utf8
sudo dpkg-reconfigure locales

mkdir -p ~/Projects/upstream

pushd ~/Projects
git clone https://github.com/victor.chong/toys.git
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
