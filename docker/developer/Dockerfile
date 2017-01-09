FROM ubuntu:16.10
MAINTAINER Daniel Thompson

RUN apt-get update && apt-get install -y \
	bc \
	build-essential \
	git \
	ncurses-dev \
	sudo \
	vim \
	tmux

RUN useradd -u 1000 -g 100 developer
COPY developer /etc/sudoers.d/

USER developer
WORKDIR /home/developer
ENTRYPOINT ["bash", "-l"]
