import cv2
import numpy as np
import sys

# ------------------------------------------------------------
# Check command-line argument
# ------------------------------------------------------------

if len(sys.argv) != 2:
    print("Usage: python coins.py image.png")
    sys.exit(1)

filename = sys.argv[1]

# ------------------------------------------------------------
# Read image
# ------------------------------------------------------------

image = cv2.imread(filename)

if image is None:
    print(f"Could not read image: {filename}")
    sys.exit(1)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray_blur = cv2.GaussianBlur(gray, (11, 11), 2)
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# ------------------------------------------------------------
# Find circles
# ------------------------------------------------------------

circles = cv2.HoughCircles(
    gray_blur,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=45,
    param1=100,
    param2=25,
    minRadius=45,
    maxRadius=75
)

if circles is None:
    print("No coins found.")
    sys.exit(1)

circles = np.round(circles[0]).astype(int)

# ------------------------------------------------------------
# Classify candidate circles
# ------------------------------------------------------------

coins = []

for x, y, r in circles:

    # Measure color only in the inner 40% of the detected circle.
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.circle(mask, (x, y), int(r * 0.4), 255, -1)

    pixels = hsv[mask > 0]

    h, s, v = pixels.mean(axis=0)

    # Reject false detections in the wood.
    if s > 150:
        continue

    # Penny
    if 5 <= h <= 30:
        denomination = "penny"

    # Silver coin
    elif 80 <= h <= 105:
        denomination = "silver"

    else:
        continue

    coins.append({
        "x": x,
        "y": y,
        "r": r,
        "h": h,
        "s": s,
        "v": v,
        "denomination": denomination
    })

# ------------------------------------------------------------
# Distinguish nickel and dime by radius
# ------------------------------------------------------------

silver_coins = [c for c in coins if c["denomination"] == "silver"]

for coin in silver_coins:
    if coin["r"] >= 65:
        coin["denomination"] = "nickel"
    else:
        coin["denomination"] = "dime"

# ------------------------------------------------------------
# Draw results
# ------------------------------------------------------------

colors = {
    "penny": (0, 0, 255),
    "nickel": (0, 255, 0),
    "dime": (255, 0, 0),
    "quarter": (0, 255, 255)
}

counts = {
    "penny": 0,
    "nickel": 0,
    "dime": 0,
    "quarter": 0
}

for coin in coins:

    denomination = coin["denomination"]
    counts[denomination] += 1

    x = coin["x"]
    y = coin["y"]
    r = coin["r"]

    color = colors[denomination]

    cv2.circle(
        image,
        (x, y),
        r,
        color,
        3
    )

    cv2.putText(
        image,
        denomination,
        (x - 35, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )

# ------------------------------------------------------------
# Calculate total
# ------------------------------------------------------------

total = (
    counts["penny"] * 0.01 +
    counts["nickel"] * 0.05 +
    counts["dime"] * 0.10 +
    counts["quarter"] * 0.25
)

# ------------------------------------------------------------
# Add small summary box
# ------------------------------------------------------------

summary = [
    f"Pennies:  {counts['penny']}",
    f"Nickels:  {counts['nickel']}",
    f"Dimes:    {counts['dime']}",
    f"Quarters: {counts['quarter']}",
    f"Total:    ${total:.2f}"
]

# Small black box in upper-left
box_x = 10
box_y = 10
line_height = 20
box_width = 145
box_height = len(summary) * line_height + 10

overlay = image.copy()

cv2.rectangle(
    overlay,
    (box_x, box_y),
    (box_x + box_width, box_y + box_height),
    (0, 0, 0),
    -1
)

# Make the box slightly transparent
cv2.addWeighted(
    overlay,
    0.65,
    image,
    0.35,
    0,
    image
)

# Small white text
for i, line in enumerate(summary):
    cv2.putText(
        image,
        line,
        (box_x + 5, box_y + 17 + i * line_height),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )

# ------------------------------------------------------------
# Print results
# ------------------------------------------------------------

print(f"Pennies:  {counts['penny']}")
print(f"Nickels:  {counts['nickel']}")
print(f"Dimes:    {counts['dime']}")
print(f"Quarters: {counts['quarter']}")
print(f"Total:    ${total:.2f}")

# ------------------------------------------------------------
# Save annotated image
# ------------------------------------------------------------

if "." in filename:
    base = filename.rsplit(".", 1)[0]
else:
    base = filename

output_filename = base + ".annotated.png"

cv2.imwrite(output_filename, image)

print(f"Saved: {output_filename}")

# ------------------------------------------------------------
# Display until window is closed
# ------------------------------------------------------------

cv2.imshow("Coins", image)

print("Close the OpenCV window to quit.")

cv2.waitKey(0)
cv2.destroyAllWindows()