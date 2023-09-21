from PIL import Image, ImageDraw
import os


TRACK_FOLDER = "map2"
OUPUT_FILE_NAME = "out_2.png"

# Read the points from the text file
points = []
markers = []

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path_1 = os.path.join(current_dir, "mapping_data" , TRACK_FOLDER, (TRACK_FOLDER + "_track_real.txt"))

out_path = os.path.join(current_dir, "mapping_data", TRACK_FOLDER, OUPUT_FILE_NAME)

with open(file_path_1, "r") as file:
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
point_size = 1

# Set the desired margin size
margin = 60

# Calculate the new dimensions with margins
new_width = width + 2 * margin
new_height = height + 2 * margin

# Create a black image with margins
image = Image.new("RGB", (new_width, new_height), "black")
draw = ImageDraw.Draw(image)

# Calculate the offset for placing the points with margins
x_offset = margin - int(min_x)
y_offset = margin - int(min_y)

# # Draw larger white points on the image with margins
for point in points:
    x = int(point[0]) + x_offset
    y = int(point[1]) + y_offset
    draw.ellipse([(x - point_size, y - point_size), (x + point_size, y + point_size)], fill="white")

# Connect the points with lines
# for i in range(1, len(points)):
#     x1 = int(points[i - 1][0]) + x_offset
#     y1 = int(points[i - 1][1]) + y_offset
#     x2 = int(points[i][0]) + x_offset
#     y2 = int(points[i][1]) + y_offset
#     draw.line([(x1, y1), (x2, y2)], fill="white", width=1)



file_path_2 = os.path.join(current_dir, "mapping_data" , TRACK_FOLDER, (TRACK_FOLDER + "_track.txt"))


points = []
with open(file_path_2, "r") as file:
    for line in file:
        x, y = line.strip().split(",")
        points.append((float(x), float(y)))



# Draw larger white points on the image with margins
for point in points:
    x = int(point[0]) + x_offset
    y = int(point[1]) + y_offset
    draw.ellipse([(x - point_size, y - point_size), (x + point_size, y + point_size)], fill="blue")




file_path_3 = os.path.join(current_dir, "mapping_data" , TRACK_FOLDER, (TRACK_FOLDER + "_track_new.txt"))

points = []
with open(file_path_3, "r") as file:
    for line in file:
        x, y = line.strip().split(",")
        points.append((float(x), float(y)))



# Draw larger white points on the image with margins
for point in points:
    x = int(point[0]) + x_offset
    y = int(point[1]) + y_offset
    draw.ellipse([(x - point_size, y - point_size), (x + point_size, y + point_size)], fill="green")








# # Draw markers
# file_path = os.path.join(current_dir, "markers.txt")
# with open(file_path, "r") as file:
#     for line in file:
#         x, y = line.strip().split(",")
#         markers.append((float(x), float(y)))


# # Calculate the offset for placing the points with margins
# x_offset = margin - int(min_x)
# y_offset = margin - int(min_y)

# # Draw larger white points on the image with margins
# for marker in markers:
#     x = int(marker[0]) + x_offset
#     y = int(marker[1]) + y_offset
#     draw.ellipse([(x - point_size, y - point_size), (x + point_size, y + point_size)], fill="blue")

# Save the image
# image.show()
image.save(out_path)