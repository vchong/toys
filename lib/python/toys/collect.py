'''
Data munging library to convert database-style records into categorized summaries.
'''

import collections

def add_percent_labels(labels, values):
	total = sum(values)
	return [ '{} ({:1.1f}%)'.format(l, 100 * (v / total)) for l, v in zip(labels, values) ]

def accumulate(things, sieve, count=lambda t: 1):
	'''Collate things into categories and count (or accumulate) them
	'''
	results = collections.defaultdict(int)
	for t in things:
		results[sieve(t)] += count(t)
	return results

def collate(things, sieve):
	'''Collate things into categories
	'''
	results = collections.defaultdict(list)
	for t in things:
		results[sieve(t)].append(t)
	return results

def rank(things):
	'''Take a sorted (k, v) sequence and add a rank to each element (r, k, v).'''
	results = []
	rank = 1
	prev_v = None
	for c, (k, v) in enumerate(things, 1):
		if v != prev_v:
			prev_v = v
			rank = c
		results.append((rank, k, v))
	return results

def simplify(things, threshold=0.005):
	total = sum(things.values())
	remaining = 0

	for k in tuple(things.keys()):
		if things[k] / total < threshold:
			remaining += things[k]
			del things[k]

	return remaining

def accumulate_2d(things, primary_sieve, secondary_sieve, count=lambda t: 1):
	'''Collate the things in two different dimensions, then count them'''
	data = collate(things, primary_sieve)
	for k in data.keys():
		data[k] = accumulate(data[k], secondary_sieve, count)
	return data
