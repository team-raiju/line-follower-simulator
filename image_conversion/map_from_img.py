import cv2
import os

INPUT_FILE_NAME = "robot-2.jpeg"
OUTPUT_FILE_NAME = "out-2.png"

# Pixel value to be considered as a black pixel 0 - 255
FILTER_THERESHOLD = 120


def main():

    # File Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_image_path = os.path.join(current_dir, "img_raw", INPUT_FILE_NAME)
    output_image_path = os.path.join(current_dir, "img_filtered", OUTPUT_FILE_NAME)

    # Load the image
    img = cv2.imread(input_image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to convert to black and white
    _, thresh = cv2.threshold(gray, FILTER_THERESHOLD, 255, cv2.THRESH_BINARY)

    # Invert colors if needed
    # inverted = cv2.bitwise_not(thresh)

    # Save the result to a file
    cv2.imwrite(output_image_path, thresh)


if __name__ == '__main__':
    main()