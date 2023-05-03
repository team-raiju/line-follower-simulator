# 1. Take a picture of the map
# 2. Crop and align img using office lens
# 3. Adjust parameters in map_from_img.py, such as input file, out file, and threshold
# 4. Run map_from_img.py to convert image to black and white
# 5. Use GIMP (or any other) to adjust small errors in generated image
# 6. Crop the image to include only the map (Image >> Crop to content in GIMP)
# 7. Generate waypoints using waypoint_from_img. Remember to edit MAP_X_SIZE_CM to contain real size of the map
# 8. Waypoints are saved in a waypoint.txt file that can be be leoaded into maps