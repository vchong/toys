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
	#vvc
	#date = subprocess.check_output(["date", "-d", s, "+%Y-%m-%d %H:%M:%S"])
	#date = str(date, 'utf-8')
	#date = date.rstrip()
	#date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
	today = datetime.date.today()
	lmon = today - datetime.timedelta(days=today.weekday(), weeks=2)
	date = str(lmon)
	#Do NOT print! Else u'll break da 'weekly' parsing
	#print("Report starting from", date)
	date = datetime.datetime.strptime(date, "%Y-%m-%d")

	# TODO: We might jump about a few hours here (date has not been
	#       told to give back values in UTC)
	date = date.replace(tzinfo=iso8601.UTC)

	if end_of_day and date.hour == 0 and date.minute == 0 and date.second == 0:
		date += datetime.timedelta(hours=23, minutes=59, seconds=59)

	return date.replace(tzinfo=iso8601.UTC)

def smart_parse2(s, end_of_day=False):
	'''Convert a string to a datetime object.

	Operates by calling out to date (because it has a good relative date
	parser).

	'''
	#vvc
	#date = subprocess.check_output(["date", "-d", s, "+%Y-%m-%d %H:%M:%S"])
	#date = str(date, 'utf-8')
	#date = date.rstrip()
	#date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
	today = datetime.date.today()
	lsun = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=-8)
	date = str(lsun)
	#Do NOT print! Else u'll break da 'weekly' parsing
	#print("Report starting from", date)
	date = datetime.datetime.strptime(date, "%Y-%m-%d")

	# TODO: We might jump about a few hours here (date has not been
	#       told to give back values in UTC)
	date = date.replace(tzinfo=iso8601.UTC)

	if end_of_day and date.hour == 0 and date.minute == 0 and date.second == 0:
		date += datetime.timedelta(hours=23, minutes=59, seconds=59)

	return date.replace(tzinfo=iso8601.UTC)

