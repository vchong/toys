ldtstool
========

Download JSON data from zendesk and provide tooling to process the JSON
into other (hopefully useful forms).

Install
-------

 * Install python3 together with modules for iso8601, matplotlib, 
   keyring and zdesk. Most modules are likely to be available in a
   similarly named distro package (e.g. python3-iso8601) but zdesk will
   probably require the use of pip3 to install.
 * Set PYTHONPATH to include $TOYSROOT/lib/python

Quickstart
----------

Firstly you must [create an API token][1](similar to App passwords in
Google) in zendesk and store it on your desktop keyring. Note that the
first time you run ldtstool you will be asked to review $HOME/.
linaro_toys and re-run; you must update this file with your own username
before re-running:

    ldtstool passwd

[1]: https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-

Now we can perform a dynamic query. Dynamic queries are fast and convenient
but will only return results from within the last three months:

    ldtstool fetch --since 'last month' | ldtstool summary

For anything going back more than three months we need to populate a
local cache containing historic data, this can only be downloaded from
the Zendesk interface:

 1. Click **Admin** (Settings wheel icon)
 2. Scroll down to **Manage** choose **Reports**
 3. Switch to the **Export** tab
 4. Select **tickets** from the **Full JSON export** row
 5. When the notification e-mail arrives, download the exported data
    and unzip it.
 6. Import that database: `ldtstool import export-????-??-??-????-*.json`

Once you have a local cache it can be updated using the pull command,
there is seldom any reason to re-import data:

    ldtstool pull --verbose
    
Finally we have an example pipeline to find out what Daniel has been
up to this month and report in markdown format `ldtstool
pull --pipe` will refresh the cache *and* share the results on the
stdout; if you want to avoid network activity then use `ldtstool dump`
instead):

    ldtstool pull --pipe | \
    ldtstool filter --assignee vchong --since 'last month' | \
    ldtstool markdown

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

    ldtstool --help

Help is also provide for each sub-command, for example:

    ldtstool filter --help

### "What did I do this week?"

    ldtstool fetch --since 'next friday -13 days' | \
    ldtstool filter --until 'next friday -7 days' --assignee vchong | \
    ldtstool weekly

### Upload your weekly activity to JIRA

This pipeline you to have configured both jira and the zendesk jiralink
property in `$HOME/.linaro_toys`. You must also have cached a suitable 
password using `glimpse passwd`.
    
    ldtstool fetch --since 'next friday -13 days' | \
    ldtstool filter --until 'next friday -7 days' --assignee vchong | \
    ldtstool worklog --time-spent 10h

### Showing overall LDTS activity

    ldtstool dump | \
    ldtstool filter --since 'today -2 years' --restrict created | \
    ldtstool chart --output chart.png
