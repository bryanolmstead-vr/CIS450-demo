# demo loading image

import cv2 as cv
import sys
import os

print("Current working directory:", os.getcwd())

img = cv.imread("photos/panorama1/IMG_0368.png")
print(img.shape)

if img is None:
    sys.exit("Could not read the image.")

cv.namedWindow("Display window", cv.WINDOW_NORMAL)
cv.resizeWindow("Display window", 800, 600)

cv.imshow("Display window", img)
k = cv.waitKey(0)

resized_image = cv.resize(img, (640, 480), dst=None, fx=None, fy=None, interpolation=cv.INTER_LINEAR)
filename = "photos/panorama1/IMG1-640x480.png"
cv.imwrite(filename, resized_image)
print(f"Image saved to {filename}")

