import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import cv2 as cv
import numpy as np
import json
import time
from pydobot import Dobot

# ---------- CAMERA CALIBRATION ----------
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

ranges = {
    "Blue": ((85,104,0),(116,255,255),(255,0,0)),
    "Green":((45,35,42),(86,255,151),(0,255,0)),
    "Yellow":((23,47,0),(38,255,255),(0,255,255)),
    "Red":((0,104,71),(6,255,255),(0,0,255),(170,150,50),(180,255,255))
}

cap = cv.VideoCapture(0)
camera_points = [None]*8
cube_names = [None]*8
ax=bx=ay=by=None

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
    cube_name_input = simpledialog.askstring("Input",
        f"Enter cube name for position {pos_index}:\nDetected: {list(centroids.keys())}")
    if cube_name_input not in centroids:
        messagebox.showwarning("Warning",f"{cube_name_input} not detected")
        return
    camera_points[pos_index] = centroids[cube_name_input]
    cube_names[pos_index] = cube_name_input
    messagebox.showinfo("Saved",f"Position {pos_index}: Cube {cube_name_input} saved at camera {centroids[cube_name_input]}")

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

def show_camera(root):
    ret, frame = cap.read()
    if ret:
        frame = cv.resize(frame,(640,480))
        detect_cubes(frame)
        cv.imshow("Camera Feed", frame)
    if cv.waitKey(1) & 0xFF != 27:
        root.after(30, lambda: show_camera(root))

def run_calibration():
    root = tk.Tk()
    root.title("8-Cube Calibration (Manual Assignment)")
    for i in range(8):
        tk.Button(root,text=f"Record Position {i}",command=lambda idx=i: record_position(idx)).pack(pady=3)
    tk.Button(root,text="Compute Mapping",command=compute_mapping).pack(pady=5)
    tk.Button(root,text="Done (Go to Stacking)",command=root.destroy).pack(pady=5)
    show_camera(root)
    root.mainloop()
    
    # Build robot_points based on dobot_positions + optional rotation
    rotations=[7,0,0,8.57648277,-1.72440433,9.97942352,0.07942359,-9.13234138]
    robot_points=[]
    for i,pos in enumerate(dobot_positions):
        d=dict(pos)
        d["r"]=rotations[i] if i<len(rotations) else 0
        d["name"]=cube_names[i]
        robot_points.append(d)
    return robot_points, cube_names

# ---------- DOBOT STACKING ----------
def run_stacking(robot_points,cube_names):
    device = Dobot(port="/dev/ttyUSB0")
    SAFE_Z = 35
    PICK_Z = -47.50025939941406
    Center_x = 245
    Center_y = 0
    Z_ERROR = 6
    place_z_levels = [-42.02153778076172-Z_ERROR, -17.51886749267578-Z_ERROR, 6.19256591796875-Z_ERROR, 32.11168670654297-Z_ERROR]
    HOME_X,HOME_Y,HOME_Z,HOME_R=245.00001525878906,0.0,120,0.07942359894514084
    stack_counter=0
    last_z=PICK_Z+SAFE_Z
    selected_cubes=[]
    def pick_and_place(cube_name):
        nonlocal stack_counter,last_z
        if stack_counter>=len(place_z_levels):
            messagebox.showinfo("Stack Full","All stack levels are already used!")
            return
        pos=next((p for p in robot_points if p["name"]==cube_name),None)
        if pos is None:
            messagebox.showerror("Error",f"No robot position found for {cube_name}")
            return
        current_z=place_z_levels[stack_counter]
        try:
            device.move_to(x=pos["x"],y=pos["y"],z=last_z,r=pos["r"])
            device.move_to(x=pos["x"],y=pos["y"],z=PICK_Z,r=pos["r"])
            device.suck(True);time.sleep(1)
            device.move_to(x=pos["x"],y=pos["y"],z=current_z+SAFE_Z,r=pos["r"])
            device.move_to(x=Center_x,y=Center_y,z=current_z+SAFE_Z,r=pos["r"])
            device.move_to(x=Center_x,y=Center_y,z=current_z,r=pos["r"]);time.sleep(1)
            device.suck(False);time.sleep(1)
            device.move_to(x=Center_x,y=Center_y,z=current_z+SAFE_Z,r=pos["r"])
            stack_counter+=1
            last_z=current_z+SAFE_Z
            print(f"{cube_name} placed at stack level {stack_counter}, next hover Z={last_z}")
        except Exception as e:
            messagebox.showerror("Error",str(e))
    def start_stacking():
        if not selected_cubes:
            messagebox.showwarning("Warning","No cubes selected!")
            return
        for cube_name in selected_cubes:
            pick_and_place(cube_name)
    def move_home():
        try:
            device.move_to(x=HOME_X,y=HOME_Y,z=HOME_Z,r=HOME_R)
        except Exception as e:
            messagebox.showerror("Error",str(e))
    def reset_dobot():
        try:
            device.home()
        except Exception as e:
            messagebox.showerror("Error",str(e))
    root=tk.Tk()
    root.title("Select 4 Cubes to Stack")
    tk.Label(root,text="Select 4 cubes (exact names) to stack:").pack(pady=5)
    cube_vars=[tk.StringVar(value=cube_names[0]) for _ in range(4)]
    for i in range(4):
        ttk.Combobox(root,values=cube_names,textvariable=cube_vars[i],state="readonly").pack(pady=3)
    def save_cubes_and_start():
        nonlocal selected_cubes
        selected_cubes=[var.get() for var in cube_vars]
        start_stacking()
    tk.Button(root,text="Start Stacking",command=save_cubes_and_start).pack(pady=10)
    tk.Button(root,text="Home (Move to Position)",command=move_home).pack(pady=5)
    tk.Button(root,text="Reset (device.home)",command=reset_dobot).pack(pady=5)
    tk.Button(root,text="Quit",command=lambda:(device.close(),root.destroy())).pack(pady=5)
    root.mainloop()

# ---------- MAIN ----------
if __name__=="__main__":
    robot_points,cube_names=run_calibration()
    run_stacking(robot_points,cube_names)
    cap.release()
    cv.destroyAllWindows()