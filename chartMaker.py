import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Create figure and axes for the flowchart
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis("off")

# Define a function to create a rounded rectangle with text
def add_box(ax, x, y, width, height, text, color):
    rect = FancyBboxPatch(
        (x, y), width, height, boxstyle="round,pad=0.3", 
        edgecolor="black", facecolor=color, lw=1.5
    )
    ax.add_patch(rect)
    ax.text(
        x + width / 2, y + height / 2, text, ha="center", va="center", 
        fontsize=10, weight="bold", color="black"
    )

# Add the boxes (steps)
add_box(ax, 3, 10, 4, 1, "Initial Path Selection", "lightblue")
add_box(ax, 1, 7.5, 4, 1, "Link Disruption Detection", "lightgreen")
add_box(ax, 5, 7.5, 4, 1, "Alternative Pathfinding", "lightyellow")
add_box(ax, 3, 5, 4, 1, "Recovery Attempts", "orange")
add_box(ax, 3, 2.5, 4, 1, "Delivery or Failure Reporting", "salmon")

# Add arrows to connect the steps
arrow_style = dict(arrowstyle="->", color="black", lw=1.5)
arrows = [
    FancyArrowPatch((5, 10), (3, 8.5), connectionstyle="arc3,rad=-0.3", **arrow_style),
    FancyArrowPatch((3, 7.5), (5, 7.5), connectionstyle="arc3,rad=0.3", **arrow_style),
    FancyArrowPatch((5, 7.5), (5, 6), connectionstyle="arc3,rad=-0.3", **arrow_style),
    FancyArrowPatch((5, 5), (5, 4), connectionstyle="arc3,rad=-0.1", **arrow_style)
]

# Add the arrows to the plot
for arrow in arrows:
    ax.add_patch(arrow)

# Show the flowchart
plt.show()

