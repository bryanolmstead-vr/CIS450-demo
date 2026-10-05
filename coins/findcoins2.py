import sys
import cv2
import numpy as np
import os

# ------------------------------------------------------------
# Get image filename from command line
# ------------------------------------------------------------

if len(sys.argv) != 2:
    print("Usage: python coins.py <image>")
    sys.exit(1)

filename = sys.argv[1]

# Create output filename
base, ext = os.path.splitext(filename)
output_filename = base + ".annotated.png"

# ------------------------------------------------------------
# Read image
# ------------------------------------------------------------

image = cv2.imread(filename)

if image is None:
    raise RuntimeError(f"Could not read {filename}")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

# ------------------------------------------------------------
# Find coins
# ------------------------------------------------------------

circles = cv2.HoughCircles(
    gray_blur,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=25,
    param1=100,
    param2=45,
    minRadius=40,
    maxRadius=100
)

if circles is None:
    raise RuntimeError("No coins detected")

circles = np.round(circles[0]).astype(int)

# Keep the four largest detected circles
if len(circles) > 4:
    circles = sorted(circles, key=lambda c: c[2], reverse=True)[:4]

# ------------------------------------------------------------
# Sort by radius
#
# Largest  -> quarter
# Next     -> nickel
# Next     -> penny
# Smallest -> dime
# ------------------------------------------------------------

circles = sorted(circles, key=lambda c: c[2], reverse=True)

coin_names = [
    "quarter",
    "nickel",
    "penny",
    "dime"
]

# OpenCV uses BGR
coin_colors = {
    "penny":   (0, 0, 255),      # red
    "nickel":  (0, 255, 0),      # green
    "dime":    (255, 0, 0),      # blue
    "quarter": (0, 255, 255)     # yellow
}

coin_values = {
    "penny": 0.01,
    "nickel": 0.05,
    "dime": 0.10,
    "quarter": 0.25
}

# ------------------------------------------------------------
# Annotate image
# ------------------------------------------------------------

total = 0

for circle, coin in zip(circles, coin_names):

    x, y, radius = circle
    color = coin_colors[coin]

    print(
        f"{coin:7s}: "
        f"center=({x}, {y}), "
        f"radius={radius}, "
        f"diameter={2 * radius}"
    )

    # Draw circle
    cv2.circle(
        image,
        (x, y),
        radius,
        color,
        3
    )

    # Draw center
    cv2.circle(
        image,
        (x, y),
        3,
        color,
        -1
    )

    # Label
    cv2.putText(
        image,
        coin,
        (x - 40, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2
    )

    total += coin_values[coin]

# ------------------------------------------------------------
# Add total
# ------------------------------------------------------------

print()
print(f"Total value: ${total:.2f}")

cv2.putText(
    image,
    f"Total: ${total:.2f}",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (255, 255, 255),
    2
)

# ------------------------------------------------------------
# Save annotated image
# ------------------------------------------------------------

cv2.imwrite(output_filename, image)

print(f"Saved annotated image: {output_filename}")

# ------------------------------------------------------------
# Display annotated image
# ------------------------------------------------------------

cv2.imshow("Coins", image)

print("Close the OpenCV window to quit.")

cv2.waitKey(0)
cv2.destroyAllWindows()