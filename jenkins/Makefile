ASCIIDOC = asciidoc
ASCIIDOCFLAGS = -a data-uri -a toc $(EXTRAASCIIDOCFLAGS)
A2X = a2x
A2XFLAGS = -dbook

CC = gcc
CFLAGS = -Wall -Os

ASCIIDOCFILES = $(wildcard *.asciidoc)
IMAGEFILES = $(wildcard images/*)
HTMLFILES = $(foreach f, $(ASCIIDOCFILES), html/$(f:.asciidoc=.html))

APPS = rdiff-backup
RDIFF_BACKUP_OBJS = rdiff-backup.o

all : $(HTMLFILES) $(APPS)

clean :
	$(RM) $(HTMLFILES) $(APPS) $(RDIFF_BACKUP_OBJS)

html/jenkins-ci.html : EXTRAASCIIDOCFLAGS=-n

rdiff-backup : $(RDIFF_BACKUP_OBJS)
	$(CC) $(CFLAGS) $(RDIFF_BACKUP_OBJS) -o $@

# sed is used to workaround a known bug in asciidoc-8.6.8 MIME type handling,
# the bug is already fixed in asciidoc mainline but not yet released.
html/%.html : %.asciidoc  $(PROCESSDOCFILES) $(INFRADOCFILES) $(IMAGEFILES)
	$(ASCIIDOC) $(ASCIIDOCFLAGS) -o $@ $<
	sed -i 's%data:image/svg;base64%data:image/svg+xml;base64%' $@

$(HTMLFILES) : html
html :
	mkdir -p html/
