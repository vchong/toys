'''
Some extra data handling utilities
'''

import datetime
import iso8601
import subprocess

def smart_parse(s, end_of_day=False):
	'''Convert a string to a datetime object.

	Operates by calling out to date (because it has a good relative date
	parser).

	'''
	try:
		date = subprocess.check_output(["date", "-d", s, "+%Y-%m-%d %H:%M:%S"])
	except subprocess.CalledProcessError as e:
		'''
		OS X date command does not follow GNU/Linux specifications
		since it is Unix and will throw the CalledProcessError exception,
		but we can make this work by installing the GNU date command as 'gdate'
		using 'brew install coreutils'.

		https://stackoverflow.com/questions/9804966/date-command-does-not-follow-linux-specifications-mac-os-x-lion
		'''
		date = subprocess.check_output(["gdate", "-d", s, "+%Y-%m-%d %H:%M:%S"])
	date = str(date, 'utf-8')
	date = date.rstrip()
	date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

	# TODO: We might jump about a few hours here (date has not been
	#       told to give back values in UTC)
	date = date.replace(tzinfo=iso8601.UTC)

	if end_of_day and date.hour == 0 and date.minute == 0 and date.second == 0:
		date += datetime.timedelta(hours=23, minutes=59, seconds=59)

	return date.replace(tzinfo=iso8601.UTC)

