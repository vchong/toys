/*
 * Use /dev/loop-control to construct loop devices.
 *
 * This allows use to simulate different CONFIG_BLK_DEV_LOOP_MIN_COUNT
 * values without recompiling the kernel. This use-case is pretty specialist
 * but does crop up when a Linux container needs access to a loop device but
 * are running older OS images (e.g. util-linux is unaware of
 * /dev/loop-control
 */

#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <linux/loop.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, const char *argv[])
{
	int res = 0;
	long num_loop = 8;

	if (argc == 2)
		num_loop = strtol(argv[1], NULL, 0);

	if (argc >= 2 || num_loop <= 0) {
		fprintf(stderr, "USAGE: loop_alloc [<num loop devices>]\n");
		return 127;
	}

	int fd = open("/dev/loop-control", O_RDWR);
	if (fd < 0) {
		fprintf(stderr, "ERROR: Cannot open /dev/loop-control: %s\n",
			strerror(errno));
		return 127;
	}

	for (long i=0; i<num_loop; i++) {
		int err = ioctl(fd, LOOP_CTL_ADD, i);
		if (err < 0) {
			fprintf(stderr,
				"ERROR: Cannot create /dev/loop%ld: %s\n", i,
				strerror(errno));
			res += 1;
		}
	}

	return res;
}
