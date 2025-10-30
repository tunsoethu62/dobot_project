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

    # --------- Step 1: detect polygons for blue ---------
    contours, _ = cv.findContours(mask_blue, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv.contourArea(cnt) > 500:
            epsilon = 0.02 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            cv.polylines(frame, [approx], True, (255,0,0), 2)
            x, y, w, h = cv.boundingRect(cnt)
            cv.putText(frame, "Blue", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

    # You can repeat the same for green, yellow, red
    contours, _ = cv.findContours(mask_green, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv.contourArea(cnt) > 500:
            epsilon = 0.02 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            cv.polylines(frame, [approx], True, (0,255,0), 2)
            x, y, w, h = cv.boundingRect(cnt)
            cv.putText(frame, "Green", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    contours, _ = cv.findContours(mask_yellow, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv.contourArea(cnt) > 500:
            epsilon = 0.02 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            cv.polylines(frame, [approx], True, (0,255,255), 2)
            x, y, w, h = cv.boundingRect(cnt)
            cv.putText(frame, "Yellow", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    contours, _ = cv.findContours(mask_red, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv.contourArea(cnt) > 500:
            epsilon = 0.02 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            cv.polylines(frame, [approx], True, (0,0,255), 2)
            x, y, w, h = cv.boundingRect(cnt)
            cv.putText(frame, "Red", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    cv.imshow("Cube Color Detection", frame)
    if cv.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv.destroyAllWindows()