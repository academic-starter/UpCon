import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
np.random.seed(10)
data = [np.random.normal(loc=0, scale=1, size=100),
        np.random.normal(loc=1, scale=1, size=100),
        np.random.normal(loc=2, scale=1, size=100)]

# Create figure and subplots
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'hspace': 0.3})

# Create boxplot for the first half of the data
bp1 = ax1.boxplot(data, labels=[0, 1, 2], widths=0.6)
ax1.set_title('Boxplot with Broken Axis')
ax1.set_ylabel('Values')

# Create boxplot for the second half of the data
bp2 = ax2.boxplot(data, labels=[0, 1, 2], widths=0.6)
ax2.set_ylabel('Values')

# Hide the top and bottom spines of the first subplot
ax1.spines['bottom'].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)

# Hide the top and bottom spines of the second subplot
ax2.spines['top'].set_visible(False)
ax2.xaxis.tick_bottom()

# Remove x-axis ticks and labels from the first subplot
plt.setp(ax1.get_xticklabels(), visible=False)

# Adjust the y-axis limits to avoid overlapping boxplots
ax1.set_ylim(-4, 4)
ax2.set_ylim(6, 10)

# Add a gap between the subplots to create the appearance of a broken axis
plt.subplots_adjust(hspace=0.05)

# Now, let's turn towards the cut-out slanted lines.
# We create line objects in axes coordinates, in which (0,0), (0,1),
# (1,0), and (1,1) are the four corners of the axes.
# The slanted lines themselves are markers at those locations, such that the
# lines keep their angle and position, independent of the axes size or scale
# Finally, we need to disable clipping.

d = .5  # proportion of vertical to horizontal extent of the slanted line
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

plt.show()
