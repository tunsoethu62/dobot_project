import cv2 as cv
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox
import json

# Video capture
cap = cv.VideoCapture(2)

# Color ranges in HSV
ranges = {
    "Blue":   ((85,104,0), (116,255,255), (255,0,0)),
    "Green":  ((45,35,42), (86,255,151), (0,255,0)),
    "Yellow": ((23,47,0), (38,255,255), (0,255,255)),
    "Red":    ((0,104,71), (6,255,255), (0,0,255)),
}

camera_points = {}
robot_points = {}
ax=bx=ay=by=None

def detect_color(frame):
    hsv = cv.cvtColor(cv.GaussianBlur(frame,(5,5),0),cv.COLOR_BGR2HSV)
    centroids = {}
    for name,(low,high,color) in ranges.items():
        mask = cv.inRange(hsv, np.array(low), np.array(high))
        contours,_ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv.contourArea(cnt) > 500:
                M = cv.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"]/M["m00"])
                    cy = int(M["m01"]/M["m00"])
                    cv.circle(frame,(cx,cy),5,color,-1)
                    cv.putText(frame,f"{name}({cx},{cy})",(cx+5,cy),cv.FONT_HERSHEY_SIMPLEX,0.5,color,2)
                    centroids[name] = (cx,cy)
    return centroids

def record_cube(color_name):
    global camera_points, robot_points
    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("Error","Camera not available")
        return
    frame = cv.resize(frame,(640,480))
    centroids = detect_color(frame)
    if color_name not in centroids:
        messagebox.showwarning("Warning",f"No {color_name} cube detected")
        return

    cx,cy = centroids[color_name]
    rx = simpledialog.askfloat("Input","Enter robot X coordinate (mm) for "+color_name)
    ry = simpledialog.askfloat("Input","Enter robot Y coordinate (mm) for "+color_name)
    camera_points[color_name] = (cx,cy)
    robot_points[color_name] = (rx,ry)
    messagebox.showinfo("Saved",f"{color_name}: Camera ({cx},{cy}) -> Robot ({rx},{ry})")

def compute_mapping():
    global ax,bx,ay,by
    if len(camera_points) < 2:
        messagebox.showwarning("Warning","Need at least 2 points to compute mapping")
        return
    u_points = np.array([camera_points[k][0] for k in camera_points])
    v_points = np.array([camera_points[k][1] for k in camera_points])
    x_points = np.array([robot_points[k][0] for k in robot_points])
    y_points = np.array([robot_points[k][1] for k in robot_points])
    A = np.vstack([u_points, np.ones(len(u_points))]).T
    ax,bx = np.linalg.lstsq(A, x_points, rcond=None)[0]
    A = np.vstack([v_points, np.ones(len(v_points))]).T
    ay,by = np.linalg.lstsq(A, y_points, rcond=None)[0]
    messagebox.showinfo("Mapping","Mapping computed:\n"
                        f"x = {ax:.4f}*u + {bx:.2f}\n"
                        f"y = {ay:.4f}*v + {by:.2f}")

def save_json():
    filename = simpledialog.askstring("Input","Enter filename to save JSON")
    if filename:
        data = {
            "camera_points": camera_points,
            "robot_points": robot_points,
            "mapping": {"ax":ax,"bx":bx,"ay":ay,"by":by}
        }
        with open(filename,"w") as f:
            json.dump(data,f,indent=2)
        messagebox.showinfo("Saved",f"Saved to {filename}")

# Tkinter GUI
root = tk.Tk()
root.title("Cube Calibration")

for color in ranges:
    btn = tk.Button(root,text=f"Record {color}",command=lambda c=color: record_cube(c))
    btn.pack(pady=5)

btn_map = tk.Button(root,text="Compute Mapping",command=compute_mapping)
btn_map.pack(pady=5)

btn_save = tk.Button(root,text="Save JSON",command=save_json)
btn_save.pack(pady=5)

btn_quit = tk.Button(root,text="Quit",command=root.quit)
btn_quit.pack(pady=5)

# Camera feed in separate thread
def show_camera():
    ret, frame = cap.read()
    if ret:
        frame = cv.resize(frame,(640,480))
        detect_color(frame)
        cv.imshow("Camera Feed", frame)
    if cv.waitKey(1) & 0xFF != 27:
        root.after(30, show_camera)

show_camera()
root.mainloop()
cap.release()
cv.destroyAllWindows()
