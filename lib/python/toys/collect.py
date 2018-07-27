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

def simplify_2d(things, threshold=0.03, category='Other', unconditional=()):
	'''Merge small values into a special category.

	Expected a dictionary of dictionaries of numbers [output of accumulate_2d()].
	'''

	# Find the largest primary category and create a list of every possible
	# secondary key
	max_sum = 0
	keys = set()
	for secondary in things.values():
		total = sum(secondary.values())
		if total > max_sum:
			max_sum = total
		keys |= set(secondary.keys())

	# Recalculate the threshold (as a fraction of the largest primary category)
	threshold = threshold * max_sum

	# Work through each secondary and remove keys that exceed the threshold
	# from the cull list
	keys_to_cull = keys
	for secondary in things.values():
		for k, v in secondary.items():
			if v >= threshold:
				keys_to_cull.discard(k)
	keys_to_cull |= set(unconditional)

	# Work through each secondary simplifying each one
	for secondary in things.values():
		for k in tuple(secondary.keys()):
			if k in keys_to_cull:
				if category not in secondary:
					secondary[category] = 0
				secondary[category] += secondary[k]
				del secondary[k]
