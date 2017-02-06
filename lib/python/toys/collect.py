'''
Data munging library to convert database-style records into categorized summaries.
'''

import collections

def add_percent_labels(labels, values):
	total = sum(values)
	return [ '{} ({:1.1f}%)'.format(l, 100 * (v / total)) for l, v in zip(labels, values) ]

def accumulate(things, sieve, count=lambda t: 1):
	'''Collate things into categories and count (or accumulate) them

	TODO: was called collect_and_count_by() in the not-yet-refactored code
	'''
	results = collections.defaultdict(int)
	for t in things:
		results[sieve(t)] += count(t)
	return results

def collate(things, sieve):
	'''Collate things into categories

	TODO: was called collect_by() in the not-yet-refactored code
	'''
	results = collections.defaultdict(list)
	for t in things:
		results[sieve(t)].append(t)
	return results

def accumulate_2d(things, primary_sieve, secondary_sieve, count=lambda t: 1):
	'''Collate the things in two different dimensions, then count them'''
	data = collate(things, primary_sieve)
	for k in data.keys():
		data[k] = accumulate(data[k], secondary_sieve, count)
	return data
