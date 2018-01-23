glance
======

Fetch data from JIRA servers and present it in a useful form.

Install
-------

 * Install python3 together with modules for iso8601, matplotlib,
   keyring and jira. Most modules are likely to be available in a
   similarly named distro package (e.g. python3-iso8601) although it
   it *not* recommended to use the distro package for jira (since it may
   be outdated and not in sync with the jira API); use pip3 for this
   module.
 * Set PYTHONPATH to include $TOYSROOT/lib/python

Quickstart
----------

Firstly you must store your jira password on your desktop keyring. Note
that the first time you run glance you may be asked to review
`$HOME/.linaro_toys` and re-run; you must update this file with your
own username before re-running:

    glance passwd

Now we can fetch data from the server and process it. The following
command will fetch tickets assigned to daniel.thompson@linaro.org if
they are open or have been modified in the last month:

    glance fetch --since 'last month' | glance summary

Generally speaking `glance fetch` will grab slightly too much data. In
particular it grabs the whole of the worklog for a ticket, not just
recent worklog entries. For this reason worklog data needs to be
filtered before it can be used. For example:

    glance fetch --since 'last month' | \
    glance filter --worklog-since  'last month' | \
    glance chart --barchart --effort-by-engineer chart.png

Dates
-----

A "smart" data parser used to parse dates supplied to --since and
--until arguments throughout the tool. The parser is implemented by
calling out to the `date` command. Assuming you have GNU date all of
the following are valid dates:

 * `yesterday`
 * `2017-08-01`
 * `last month`
 * `next friday -1 week` - this is similar to `last friday` but if run *on* a
   Friday will give today rather than last week

See `man date` for more details!

Examples
--------

### Getting help

Using --help will provide help on all available sub-commands:

    glance --help

Help is also provide for each sub-command, for example:

    glance fetch --help
    
### "What did I do this week?"

    glance fetch --since 'next friday -13 days' | \
    glance filter --assignee daniel --no-worklog \
            --worklog-since 'next friday -13 days' \
            --worklog-until 'next friday -7 days' \
    | glance weekly

### Show overall JIRA activity

    glance fetch --since 'today -2 years' | \
    glance filter --worklog-since 'today -2 years' | \
    glance chart --effort-by-member member.png --effort-by-component comp.png
