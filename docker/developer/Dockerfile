FROM ubuntu:16.04
MAINTAINER Daniel Thompson

RUN apt-get update && apt-get install \
	sudo

RUN useradd -u 1000 -g 100 developer
ADD developer /etc/sudoers.d/
USER developer

ENTRYPOINT ["bash", "-l"]
