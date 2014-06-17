/*
 * rdiff-backup.c
 *
 * SUID wrapper around rdiff-backup to allow usage from jenkins.
 */

#define _GNU_SOURCE

#include <assert.h>
#include <getopt.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void verify_failed(const char *t)
{
	fprintf(stderr, "ERROR: Security check failed: %s\n", t);
	exit(1);
}

#define verify(x)                                                              \
	do {                                                                   \
		if (!(x))                                                      \
			verify_failed(#x);                                     \
	} while (0)

void scrub_environment(void)
{
	clearenv();
	putenv("PATH=/bin:/usr/bin");
}

char *xstrdup_printf(const char *fmt, ...)
{
	va_list ap;

	va_start(ap, fmt);
	int len = vsnprintf(NULL, 0, fmt, ap);
	va_end(ap);

	char *s = malloc(len+1);
	if (!s) {
		fprintf(stderr, "ERROR: Cannot allocate memory\n");
		exit(2);
	}

	va_start(ap, fmt);
	vsprintf(s, fmt, ap);
	va_end(ap);

	return s;
}

int main(int argc, char * const argv[])
{
	char *verbosity = NULL;

	scrub_environment();

	int c;
	static struct option long_options[] = {
		{"verbosity", required_argument, 0, 'v'},
		{ 0 }
	};
	while (-1 != (c = getopt_long(argc, argv, "v:", long_options, NULL))) {
		switch(c) {
		case 'v':
			verbosity =
			    xstrdup_printf("--verbosity=%d", atoi(optarg));
			break;
		default:
			verify_failed("bad argument(s)");
			break;
		}
	}

	verify(argc - optind == 2);

	char *source = argv[optind];
	char *dest = argv[optind+1];

#define VALIDATE(s, d) \
	do if (0 == strcmp(source, s)) { \
		verify(0 == strcmp(dest, d)); \
		valid = true; \
	} while(0)

	bool valid = false;
	VALIDATE("/home", "/backup/home");
	VALIDATE("/sandpit/sundance", "/backup/sandpit/sundance");
	VALIDATE("harvey:/sandpit/harvey", "/backup/sandpit/harvey");
	if (!valid)
		verify_failed("invalid source directory");

	char *eargv[5];
	int eargc = 0;
	eargv[eargc++] = "/usr/bin/rdiff-backup";
	if (verbosity)
		eargv[eargc++] = verbosity;
	eargv[eargc++] = source;
	eargv[eargc++] = dest;
	eargv[eargc] = NULL;
	assert(eargc < (sizeof(eargv) / sizeof(eargv[0])));

	execv("/usr/bin/rdiff-backup", eargv);
	/* not reached */

	return 0;
}
