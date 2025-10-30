import cv2 as cv
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox
import json

# Dobot positions: 0-7
dobot_positions = [
    {"x":282.28366, "y":36.58863},
    {"x":281.34490, "y":4.02974},
    {"x":280.39285, "y":-29.90688},
    {"x":244.78771, "y":36.91789},
    {"x":242.74148, "y":-33.28932},
    {"x":209.05445, "y":36.78453},
    {"x":210.73004, "y":0.29211},
    {"x":209.27142, "y":-33.64101}
]

# Camera setup
cap = cv.VideoCapture(0)

# HSV ranges
ranges = {
    "Blue": ((85,104,0),(116,255,255),(255,0,0)),
    "Green":((45,35,42),(86,255,151),(0,255,0)),
    "Yellow":((23,47,0),(38,255,255),(0,255,255)),
    "Red":((0,104,71),(6,255,255),(0,0,255),(170,150,50),(180,255,255))
}

# Stores assigned cube names and camera coordinates
camera_points = [None]*8
cube_names = [None]*8
ax=bx=ay=by=None

# Detect cubes in frame
def detect_cubes(frame):
    centroids = {}
    hsv = cv.cvtColor(cv.GaussianBlur(frame,(5,5),0),cv.COLOR_BGR2HSV)
    for name, vals in ranges.items():
        if name != "Red":
            low, high, color = vals
            mask = cv.inRange(hsv,np.array(low),np.array(high))
        else:
            low1, high1, color, low2, high2 = vals
            mask = cv.inRange(hsv,np.array(low1),np.array(high1)) | cv.inRange(hsv,np.array(low2),np.array(high2))
        contours,_ = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        count = 0
        for cnt in contours:
            if cv.contourArea(cnt)>500:
                M = cv.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"]/M["m00"])
                    cy = int(M["m01"]/M["m00"])
                    cv.circle(frame,(cx,cy),5,color,-1)
                    label = f"{name}{count+1}"
                    cv.putText(frame,label,(cx+5,cy),cv.FONT_HERSHEY_SIMPLEX,0.5,color,2)
                    centroids[label] = (cx,cy)
                    count += 1
    return centroids

# Record a cube for a Dobot position
def record_position(pos_index):
    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("Error","Camera not available")
        return
    frame = cv.resize(frame,(640,480))
    centroids = detect_cubes(frame)
    if not centroids:
        messagebox.showwarning("Warning","No cube detected")
        return
    # Ask which cube to assign
    cube_name_input = simpledialog.askstring(
        "Input",
        f"Enter cube name for position {pos_index}:\nDetected: {list(centroids.keys())}"
    )
    if cube_name_input not in centroids:
        messagebox.showwarning("Warning",f"{cube_name_input} not detected")
        return
    camera_points[pos_index] = centroids[cube_name_input]
    cube_names[pos_index] = cube_name_input
    messagebox.showinfo("Saved",f"Position {pos_index}: Cube {cube_name_input} saved at camera {centroids[cube_name_input]}")

# Compute mapping from camera to Dobot
def compute_mapping():
    global ax,bx,ay,by
    valid_points = [(camera_points[i],dobot_positions[i]) for i in range(8) if camera_points[i] is not None]
    if len(valid_points)<2:
        messagebox.showwarning("Warning","Need at least 2 points to compute mapping")
        return
    u_points = np.array([p[0][0] for p in valid_points])
    v_points = np.array([p[0][1] for p in valid_points])
    x_points = np.array([p[1]["x"] for p in valid_points])
    y_points = np.array([p[1]["y"] for p in valid_points])
    A = np.vstack([u_points,np.ones(len(u_points))]).T
    ax,bx = np.linalg.lstsq(A,x_points,rcond=None)[0]
    A = np.vstack([v_points,np.ones(len(v_points))]).T
    ay,by = np.linalg.lstsq(A,y_points,rcond=None)[0]
    messagebox.showinfo("Mapping","Mapping computed:\n"
                        f"x = {ax:.4f}*u + {bx:.2f}\n"
                        f"y = {ay:.4f}*v + {by:.2f}")

# Save JSON
def save_json():
    filename = simpledialog.askstring("Input","Enter filename to save JSON")
    if filename:
        data = {
            "camera_points": camera_points,
            "cube_names": cube_names,
            "robot_points": dobot_positions,
            "mapping": {"ax":ax,"bx":bx,"ay":ay,"by":by}
        }
        with open(filename,"w") as f:
            json.dump(data,f,indent=2)
        messagebox.showinfo("Saved",f"Saved to {filename}")

# Tkinter GUI
root = tk.Tk()
root.title("8-Cube Calibration (Manual Assignment)")

for i in range(8):
    btn = tk.Button(root,text=f"Record Position {i}",command=lambda idx=i: record_position(idx))
    btn.pack(pady=3)

btn_map = tk.Button(root,text="Compute Mapping",command=compute_mapping)
btn_map.pack(pady=5)

btn_save = tk.Button(root,text="Save JSON",command=save_json)
btn_save.pack(pady=5)

btn_quit = tk.Button(root,text="Quit",command=root.quit)
btn_quit.pack(pady=5)

# Show camera feed with detections
def show_camera():
    ret, frame = cap.read()
    if ret:
        frame = cv.resize(frame,(640,480))
        detect_cubes(frame)
        cv.imshow("Camera Feed", frame)
    if cv.waitKey(1) & 0xFF != 27:
        root.after(30, show_camera)

show_camera()
root.mainloop()
cap.release()
cv.destroyAllWindows()