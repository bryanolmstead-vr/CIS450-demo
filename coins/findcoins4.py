import cv2
import numpy as np
import sys
import os


DIAMETERS = {
    "penny": 19.05,
    "nickel": 21.21,
    "dime": 17.91,
    "quarter": 24.26,
}

VALUES = {
    "penny": 0.01,
    "nickel": 0.05,
    "dime": 0.10,
    "quarter": 0.25,
}

COLORS = {
    "penny": (0, 0, 255),       # Red
    "nickel": (0, 200, 0),      # Green
    "dime": (255, 0, 0),        # Blue
    "quarter": (0, 220, 255),   # Yellow
}


def remove_nested_circles(circles):
    """Remove smaller circles that are probably inside larger coins."""

    circles = sorted(circles, key=lambda c: c[2], reverse=True)

    result = []

    for x, y, r in circles:
        reject = False

        for x2, y2, r2 in result:
            distance = np.hypot(x - x2, y - y2)

            if r < 0.85 * r2 and distance < 0.60 * r2:
                reject = True
                break

        if not reject:
            result.append((x, y, r))

    return result


def detect_coins(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=25,
        param1=100,
        param2=28,
        minRadius=30,
        maxRadius=50,
    )

    if circles is None:
        return []

    circles = np.round(circles[0]).astype(int)

    circles = remove_nested_circles(circles)

    return circles


def is_penny(image, x, y, r):
    """Determine whether a coin has the copper color of a penny."""

    h, w = image.shape[:2]

    x1 = max(0, x - int(r * 0.6))
    x2 = min(w, x + int(r * 0.6))
    y1 = max(0, y - int(r * 0.6))
    y2 = min(h, y + int(r * 0.6))

    roi = image[y1:y2, x1:x2]

    if roi.size == 0:
        return False

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower = np.array([5, 50, 40])
    upper = np.array([30, 255, 220])

    mask = cv2.inRange(hsv, lower, upper)

    copper_fraction = np.mean(mask > 0)

    return copper_fraction > 0.20


def classify_coins(image, circles):
    """Classify each detected coin."""

    if len(circles) == 0:
        return []

    # First identify pennies from color.
    penny_indices = []

    for i, (x, y, r) in enumerate(circles):
        if is_penny(image, x, y, r):
            penny_indices.append(i)

    # Estimate pixel/mm scale from pennies if possible.
    if penny_indices:
        penny_radii = [circles[i][2] for i in penny_indices]
        pixel_diameter = np.median(penny_radii) * 2
        pixels_per_mm = pixel_diameter / DIAMETERS["penny"]

    else:
        pixel_diameters = [r * 2 for _, _, r in circles]
        pixels_per_mm = np.median(pixel_diameters) / 21.0

    results = []

    for i, (x, y, r) in enumerate(circles):

        if i in penny_indices:
            denomination = "penny"

        else:
            measured_diameter_mm = (2 * r) / pixels_per_mm

            denomination = min(
                ("nickel", "dime", "quarter"),
                key=lambda name:
                    abs(measured_diameter_mm - DIAMETERS[name])
            )

        results.append((x, y, r, denomination))

    return results


def annotate(image, coins):

    output = image.copy()

    counts = {
        "penny": 0,
        "nickel": 0,
        "dime": 0,
        "quarter": 0,
    }

    total = 0.0

    # Draw each detected coin.
    for x, y, r, denomination in coins:

        color = COLORS[denomination]

        cv2.circle(
            output,
            (x, y),
            r,
            color,
            3
        )

        # Put denomination label inside the circle.
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1

        (text_width, text_height), _ = cv2.getTextSize(
            denomination,
            font,
            font_scale,
            thickness
        )

        text_x = x - text_width // 2
        text_y = y + text_height // 2

        cv2.putText(
            output,
            denomination,
            (text_x, text_y),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )

        counts[denomination] += 1
        total += VALUES[denomination]

    # ---------------------------------------------------------
    # Summary box
    # ---------------------------------------------------------

    lines = [
        f"Pennies:  {counts['penny']}",
        f"Nickels:  {counts['nickel']}",
        f"Dimes:    {counts['dime']}",
        f"Quarters: {counts['quarter']}",
        f"Total:    ${total:.2f}",
    ]

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 1
    padding = 8
    line_height = 18

    max_width = 0

    for line in lines:
        (width, height), _ = cv2.getTextSize(
            line,
            font,
            font_scale,
            thickness
        )

        max_width = max(max_width, width)

    box_width = max_width + 2 * padding
    box_height = len(lines) * line_height + 2 * padding

    x0 = 10
    y0 = 10

    # Slightly transparent white background.
    overlay = output.copy()

    cv2.rectangle(
        overlay,
        (x0, y0),
        (x0 + box_width, y0 + box_height),
        (255, 255, 255),
        -1
    )

    output = cv2.addWeighted(
        overlay,
        0.75,
        output,
        0.25,
        0
    )

    # Draw summary text.
    for i, line in enumerate(lines):

        y = y0 + padding + (i + 1) * line_height - 3

        cv2.putText(
            output,
            line,
            (x0 + padding, y),
            font,
            font_scale,
            (0, 0, 0),
            thickness,
            cv2.LINE_AA
        )

    return output


def main():

    if len(sys.argv) != 2:
        print("Usage: python findcoins4.py coins4.png")
        return

    input_file = sys.argv[1]

    image = cv2.imread(input_file)

    if image is None:
        print(f"Could not read image: {input_file}")
        return

    # Detect coins.
    circles = detect_coins(image)

    print(f"Detected {len(circles)} circles")

    # Classify coins.
    coins = classify_coins(image, circles)

    # Annotate image.
    output = annotate(image, coins)

    # Create output filename.
    base, ext = os.path.splitext(input_file)
    output_file = base + ".annotated.png"

    cv2.imwrite(output_file, output)

    print(f"Saved: {output_file}")

    # Print results.
    counts = {
        "penny": 0,
        "nickel": 0,
        "dime": 0,
        "quarter": 0,
    }

    total = 0.0

    for _, _, _, denomination in coins:
        counts[denomination] += 1
        total += VALUES[denomination]

    print()
    print("Coin summary:")
    print(f"  Pennies:  {counts['penny']}")
    print(f"  Nickels:  {counts['nickel']}")
    print(f"  Dimes:    {counts['dime']}")
    print(f"  Quarters: {counts['quarter']}")
    print(f"  Total:    ${total:.2f}")

    # Display the annotated image.
    cv2.imshow("Coins", output)

    print()
    print("Close the OpenCV window to quit.")

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()