FROM ubuntu:16.04
MAINTAINER Daniel Thompson

RUN apt-get update
RUN apt-get -y upgrade

RUN useradd -u 1000 -g 100 developer

RUN apt-get -y install sudo
ADD developer /etc/sudoers.d/

USER developer
ENTRYPOINT ["bash", "-l"]
