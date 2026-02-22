import cv2
import numpy as np

# Load the image
img_path = 'coins.png'
img = cv2.imread(img_path)

if img is None:
    print(f"Could not load image from {img_path}")
    exit(1)

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(gray, (9, 9), 0)

# Detect circles using Hough Circle Detection
circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=70,   # Minimum distance between circle centers
    param1=130,   # Upper threshold for Canny edge detection
    param2=75,    # Threshold for center accumulation
    minRadius=38,
    maxRadius=110
)

# Convert to HSV for better color detection
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Count and display results
if circles is not None:
    circles = np.uint16(np.around(circles))
    
    # Filter circles by copper color
    penny_count = 0
    img_with_circles = img.copy()
    
    for i in circles[0, :]:
        center = (i[0], i[1])
        radius = i[2]
        
        # Extract the region of interest (the coin)
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, -1)
        
        # Get the average HSV values within the coin
        coin_region = hsv[mask == 255]
        if len(coin_region) > 0:
            avg_h = np.mean(coin_region[:, 0])
            avg_s = np.mean(coin_region[:, 1])
            avg_v = np.mean(coin_region[:, 2])
            
            # Copper pennies have high saturation, silver coins have low saturation
            is_copper = avg_s > 100
            
            if is_copper:
                penny_count += 1
                # Draw green circle for pennies
                cv2.circle(img_with_circles, center, radius, (0, 255, 0), 5)
                cv2.circle(img_with_circles, center, 2, (0, 255, 0), 3)
    
    print(f"Number of pennies detected: {penny_count}")
    
    # Save the result image
    cv2.imwrite('coins_detected.png', img_with_circles)
    print("Result saved to coins_detected.png")
else:
    print("No coins detected")

# Display image info
height, width = img.shape[:2]
print(f"Image dimensions: {width}x{height}")
