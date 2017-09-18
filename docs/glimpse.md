glimpse
=======

Fetch data from JIRA servers and present it in a useful form.

Note: `glimpse` is *much* less flexible than `ldtstool` and `96btool`.
      It does not utilize a JSON-based interchange format, instead
      most of the commands are fixed function and it cannot be
      composed using pipes.

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
that the first time you run glimpse you may be asked to review
`$HOME/.linaro_toys` and re-run; you must update this file with your
own username before re-running:

    glimpse passwd

Now we can generate a template for your weekly report. Be aware the time
window glimpse uses is wider than seven days (to help you if you don't
do your weekly report on exactly the right day each week). The resulting
template may need to be trimmed (and augmented with other useful things
you might have done this week that are not reported in JIRA):

    glimpse weekly assignee = victor.chong@linaro.org

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

    glimpse --help

Help is also provide for each sub-command, for example:

    glimpse weekly --help
