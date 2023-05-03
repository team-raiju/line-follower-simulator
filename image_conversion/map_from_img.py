import cv2

# Load the image
img = cv2.imread('/home/marco/Documents/Projetos/raijin/line-follower-ml/image_conversion/rsm-2023.jpg')

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply thresholding to convert to black and white
_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

# Save the result to a file
cv2.imwrite('filter-rsm-2023.jpg', thresh)