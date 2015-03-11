CC = gcc
CFLAGS = -g -Os -Wall -std=gnu11
OBJS = loop-alloc.o

loop-alloc : $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

clean :
	$(RM) loop-alloc $(OBJS)
