import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# Create figure and axes for the circular diagram
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# Define positions for components in a circular layout
positions = [
    (5, 8),  # Network Simulator
    (8, 5),  # Routing Algorithm
    (5, 2),  # DTN Core
    (2, 5),  # Visualization
    (5, 5)   # Analyzer (center)
]

labels = [
    "Network Simulator",
    "Routing Algorithm",
    "DTN Core",
    "Visualization",
    "Analyzer"
]

colors = [
    "lightblue",  # Network Simulator
    "lightgreen",  # Routing Algorithm
    "lightcoral",  # DTN Core
    "lightyellow",  # Visualization
    "lightgray"    # Analyzer
]

# Draw circles for each component
for pos, label, color in zip(positions, labels, colors):
    circle = Circle(pos, radius=1.5, edgecolor="black", facecolor=color, lw=1.5)
    ax.add_patch(circle)
    ax.text(pos[0], pos[1], label, ha="center", va="center", fontsize=10, weight="bold")

# Display the circular diagram
plt.show()
