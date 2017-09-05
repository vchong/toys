'''
Simplified charting library based on matplotlib.

Works best with data sets prepared using toys.collect
'''

import hashlib
import matplotlib.pyplot as plt

import toys.collect as collect

def get_colour(s):
	override = {
		'lava' : 'orange',
		'LAVA' : 'orange',
		'96boards' : 'red',
		'96Boards' : 'red',
                # Daniel Thompson and Leo Yan both hash orange
                'Daniel Thompson' : 'green',
	}

	if s in override:
		return override[s]

	return '#{}'.format(hashlib.md5(str(s).encode('UTF-8')).hexdigest()[-6:])

def stacked_barchart(things, filename, title=None, xlabel=None, ylabel=None):
	x_labels = sorted(things.keys())

	legend_labels = set()
	for y in things.values():
		legend_labels |= set(y.keys())
	legend_labels = sorted(legend_labels)

	plots = []
	left = range(len(x_labels))

	# Working in reverse order allows us to stack things so that the
	# (alphabetic) legend is geometrically consistant with the stacks
	# on the charts.
	cumulative_height = [ 0 for x in x_labels ]
	for y in sorted(legend_labels, reverse=True):
		values = [ things[x][y] for x in x_labels ]
		plots.append(plt.bar(left, values, 1,
			bottom=cumulative_height, color=get_colour(y), edgecolor='black'))
		cumulative_height = [ c+v for c, v in zip(cumulative_height,
							  values) ]

	# Now we must reverse plots in order to match it back up with the
	# legend labels
	plots.reverse()

	if title:
		plt.title(title)
	if xlabel:
		plt.xlabel(xlabel)
	if ylabel:
		plt.ylabel(ylabel)

	plt.xticks([ x+0.5 for x in left ], x_labels, rotation=90)
	lgd = plt.legend(plots, legend_labels, bbox_to_anchor=(1.05, 1), loc=2)
	plt.savefig(filename, bbox_extra_artists=(lgd,), bbox_inches='tight')
	plt.close()

def piechart(things, filename, title=None):
	labels = sorted(things.keys())
	counts = [ things[l] for l in labels ]
	colours = [ get_colour(l) for l in labels ]

	wedges, texts = plt.pie(counts, colors=colours, startangle=90)
	for w in wedges:
		w.set_edgecolor('black')
	plt.legend(wedges, collect.add_percent_labels(labels, counts), loc="best")
	plt.axis('equal')
	if title:
		plt.suptitle(title, fontsize=14)
	plt.tight_layout()
	plt.savefig(filename)
	plt.close()
