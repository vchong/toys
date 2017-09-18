96btool
=======

Download post data from the forum, convert to JSON and provide tooling
to process the JSON into other (hopefully useful forms).

Install
-------

 * Install python3 together with modules for iso8601, matplotlib,
   keyring and pydiscourse. Most modules are likely to be available in a
   similarly named distro package (e.g. python3-iso8601) but pydiscourse
   will probably require the use of pip3 to install.
 * Set PYTHONPATH to include $TOYSROOT/lib/python

Quickstart
----------

Firstly let try a dynamic query. Dynamic queries are fast and convenient
but are limited to returning only 50 posts (you may be asked to review
$HOME/.linaro_toys and re-run; this will only happen once):

    96btool fetch --query bluetooth --since 'last month' | 96btool summary

For anything more than quick queries we need to build a local cache.
Fetching the initial data from scratch is possible but it takes *ages*.
Instead it is recommended that you pre-populate the cache:

    curl https://people.linaro.org/~victor.chong/96btool-20170907.db.xz | \
        unxz -c > $TOYSROOT/96btool.db

Having done that the initial pull will be much quicker although it will
take long enough that we value --verbose showing us signs of progress:

    96btool pull --verbose

Finally we have an example pipeline to "who are the most prolific post
authors this month". This command takes the very common form of a
src/filter/sink pipeline. Most useful pipelines have this form (`96btool
pull --pipe` will refresh the cache *and* share the results on the
stdout; if you want to avoid network activity then use `96btool dump`
instead):

    96btool pull --pipe | \
    96btool filter --since 'last month' | \
    96btool count --by-user --rank --text | \
    head

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

    96btool --help

Help is also provide for each sub-command, for example:

    96btool filter --help

### "What did I do this week?"

    96btool pull --pipe | \
    96btool filter \
        --since 'next friday -13 days' \
        --until 'next friday -7 days' \
        --user vchong | \
    96btool weekly

### Upload your weekly activity to JIRA

This pipeline you to have configured both jira and the zendesk jiralink
property in `$HOME/.linaro_toys`. You must also have cached a suitable
password using `glimpse passwd`.

    96btool pull --pipe | \
    96btool filter \
        --since 'next friday -13 days' \
        --until 'next friday -7 days' \
        --user vchong | \
    96btool worklog --time-spent 10h

### What is the most popular board this month?

    96btool dump | \
    96btool filter --since last-month | \
    96btool count --by-category --rank --text

It is also possible to visualize this information as a piechart:

    96btool dump | \
    96btool filter --since last-month | \
    96btool count --by-category | \
    96btool piechart --output chart.png

### Showing overall forum health

    96btool dump | \
    96btool filter --since 'today -2 years' | \
    96btool chart --output chart.png

With small changes to the filter this can also summarize the effort by
particular individuals or groups:

    96btool dump | \
    96btool filter --since 'today -2 years' --user vchong,sdrobertw | \
    96btool chart --output chart.png



