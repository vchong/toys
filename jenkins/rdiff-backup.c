/*
 * rdiff-backup.c
 *
 * SUID wrapper around rdiff-backup to allow usage from jenkins.
 */

#define _GNU_SOURCE

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define verify(x) do_verify(x, #x)

void do_verify(bool c, const char *t)
{
	if (!c) {
		fprintf(stderr, "ERROR: Security check failed: %s\n", t);
		exit(1);
	}
}

void scrub_environment(void)
{
	clearenv();
	putenv("PATH=/bin:/usr/bin");
}

int main(int argc, const char *argv[])
{
	scrub_environment();

	verify(argc == 3);

	const char *source = argv[1];
	const char *dest = argv[2];

#define VALIDATE(s, d) \
	do if (0 == strcmp(argv[1], s)) { \
		verify(0 == strcmp(argv[2], d)); \
		valid = true; \
	} while(0)

	bool valid = false;
	VALIDATE("/home", "/backup/home");
	VALIDATE("/sandpit/sundance", "/backup/sandpit/sundance");
	VALIDATE("harvey:/sandpit/harvey", "/backup/sandpit/harvey");
	verify(valid);

	execl("rdiff-backup", "/usr/bin/rdiff-backup",
			 source, dest, NULL);
	/* not reached */

	return 0;
}
