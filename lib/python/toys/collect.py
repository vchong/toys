'''
Data munging library to convert database-style records into categorized summaries.
'''

import collections

def add_percent_labels(labels, values):
	total = sum(values)
	return [ '{} ({:1.1f}%)'.format(l, 100 * (v / total)) for l, v in zip(labels, values) ]

def collect_by(things, categorize):
	results = collections.defaultdict(list)
	for t in things:
		results[categorize(t)].append(t)
	return results

def collect_and_count_by(things, categorize, count=lambda t: 1):
	results = collections.defaultdict(int)
	for t in things:
		results[categorize(t)] += count(t)
	return results
