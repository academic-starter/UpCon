import matplotlib.pyplot as plt
import numpy as np

# Sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Create the figure and the primary y-axis
fig, ax1 = plt.subplots()

# Plot the first dataset on the primary y-axis
ax1.plot(x, y1, 'b-', label='sin(x)')
ax1.set_xlabel('X axis')
ax1.set_ylabel('sin(x)', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# Create the secondary y-axis
ax2 = ax1.twinx()

# Plot the second dataset on the secondary y-axis
ax2.plot(x, y2, 'r-', label='cos(x)')
ax2.set_ylabel('cos(x)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

# Add legends for both y-axes
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Set x-axis range
ax1.set_xlim([0, 10])

# Show the plot
plt.title('Plot with Multiple Y-Axes')
plt.show()
