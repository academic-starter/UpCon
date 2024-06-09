import matplotlib.pyplot as plt
import numpy as np

# Sample data
categories = ['Category 1', 'Category 2', 'Category 3']
subcategories = ['A', 'B', 'C']
data = {
    'Category 1': [5, 7, 3],
    'Category 2': [2, 4, 6],
    'Category 3': [8, 5, 9]
}

# Number of categories and subcategories
num_categories = len(categories)
num_subcategories = len(subcategories)

# Positions of the bars on the x-axis
bar_width = 0.2
positions = np.arange(num_categories)

# Create the figure and axes
fig, ax = plt.subplots()

# Plot each subcategory
for i, subcategory in enumerate(subcategories):
    values = [data[category][i] for category in categories]
    ax.bar(positions + i * bar_width, values, bar_width, label=subcategory)

# Add labels, title, and legend
ax.set_xlabel('Categories')
ax.set_ylabel('Values')
ax.set_title('Bar Chart for Multiple X-Dimensions')
ax.set_xticks(positions + bar_width * (num_subcategories - 1) / 2)
ax.set_xticklabels(categories)
ax.legend(title='Subcategories')

# Show the plot
plt.show()
