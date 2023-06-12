from PIL import Image, ImageDraw
import os

# Read the points from the text file
points = []

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "map6_track.txt")

out_path = os.path.join(current_dir, "out.png")

with open(file_path, "r") as file:
    for line in file:
        x, y = line.strip().split(",")
        points.append((float(x), float(y)))

# Determine the image dimensions based on the points
min_x = min(point[0] for point in points)
max_x = max(point[0] for point in points)
min_y = min(point[1] for point in points)
max_y = max(point[1] for point in points)
width = int(max_x - min_x) + 1
height = int(max_y - min_y) + 1

# Set the desired point size
point_size = 3

# Set the desired margin size
margin = 20

# Calculate the new dimensions with margins
new_width = width + 2 * margin
new_height = height + 2 * margin

# Create a black image with margins
image = Image.new("RGB", (new_width, new_height), "black")
draw = ImageDraw.Draw(image)

# Calculate the offset for placing the points with margins
x_offset = margin - int(min_x)
y_offset = margin - int(min_y)

# Draw larger white points on the image with margins
for point in points:
    x = int(point[0]) + x_offset
    y = int(point[1]) + y_offset
    draw.ellipse([(x - point_size, y - point_size), (x + point_size, y + point_size)], fill="white")

# Connect the points with lines
for i in range(1, len(points)):
    x1 = int(points[i - 1][0]) + x_offset
    y1 = int(points[i - 1][1]) + y_offset
    x2 = int(points[i][0]) + x_offset
    y2 = int(points[i][1]) + y_offset
    draw.line([(x1, y1), (x2, y2)], fill="white", width=1)
# Save the image
image.save(out_path)