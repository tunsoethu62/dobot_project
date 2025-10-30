import cv2 as cv
import numpy as np

cap = cv.VideoCapture(2)

# Color ranges in HSV
lower_blue = np.array([85, 104, 0])
upper_blue = np.array([116, 255, 255])

lower_green = np.array([45, 35, 42])
upper_green = np.array([86, 255, 151])

lower_yellow = np.array([23, 47, 0])
upper_yellow = np.array([38, 255, 255])

# Red ranges
lower_red1 = np.array([0, 104, 71])
upper_red1 = np.array([6, 255, 255])
lower_red2 = np.array([170, 150, 50])
upper_red2 = np.array([180, 255, 255])

def detect_color(mask, frame, color_name, draw_color):
    """Find contours, draw centroid and label."""
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv.contourArea(cnt) > 500:  # filter small noise
            # Draw contour
            cv.drawContours(frame, [cnt], -1, draw_color, 2)

            # Compute centroid using moments
            M = cv.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Draw centroid
                cv.circle(frame, (cx, cy), 5, draw_color, -1)
                # Label
                cv.putText(frame, f"{color_name} ({cx},{cy})", (cx + 10, cy),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 2)
                print(f"{color_name} centroid at: ({cx}, {cy})")
            else:
                # In case of division by zero
                pass

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.resize(frame, (640, 480))
    blur = cv.GaussianBlur(frame, (5,5), 0)
    hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)

    # Create masks
    mask_blue = cv.inRange(hsv, lower_blue, upper_blue)
    mask_green = cv.inRange(hsv, lower_green, upper_green)
    mask_yellow = cv.inRange(hsv, lower_yellow, upper_yellow)
    mask_red = cv.inRange(hsv, lower_red1, upper_red1) | cv.inRange(hsv, lower_red2, upper_red2)

    # Detect each color
    detect_color(mask_blue, frame, "Blue", (255,0,0))
    detect_color(mask_green, frame, "Green", (0,255,0))
    detect_color(mask_yellow, frame, "Yellow", (0,255,255))
    detect_color(mask_red, frame, "Red", (0,0,255))

    cv.imshow("Cube Color Detection", frame)
    if cv.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv.destroyAllWindows()
