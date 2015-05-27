/*
 * rdiff-backup.c
 *
 * SUID wrapper around rdiff-backup to allow usage from jenkins.
 */

#define _GNU_SOURCE

#include <assert.h>
#include <getopt.h>
#include <libgen.h>
#include <limits.h>
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
	putenv("PATH=/sbin:/bin:/usr/sbin:/usr/bin");
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
	scrub_environment();
	verify(argc == 1);

	/* grab the location of this executable (we cannot trust argv[0]) */
	pid_t pid = getpid();
	char *procexe = xstrdup_printf("/proc/%d/exe", pid);
	char exe[PATH_MAX];
	ssize_t len = readlink(procexe, exe, sizeof(exe)-1);
	free(procexe);
	verify(len > 0);
	exe[len] = '\0';
	char *dir = dirname(exe);

#if 0
	/* derive the name of the executable we must launch */
	char *tm = xstrdup_printf("%s/time_machine", dir);
	
	/* prepare to load new image */
	char *eargv[2];
	int eargc = 0;
	eargv[eargc++] = tm;
	eargv[eargc] = NULL;
	assert(eargc < (sizeof(eargv) / sizeof(eargv[0])));

	/* change effective uid/gid (otherwise ruby sub-processes will not
	 * have root access)
	 */
	verify(seteuid(0) == 0);
	verify(setegid(0) == 0);

	execv(tm, eargv);
	fprintf(stderr, "ERROR: Failed to load new process image\n");
	return 1;
#else
	nt res = system(xstrdup_printf("su -c %s/time_machine", dir));
	return res;
#endif
}
