import tkinter as tk
from tkinter import messagebox
from pydobot import Dobot
import time
import json

# Load calibrated JSON from OpenCV calibration
with open("calliberated", "r") as f:
    data = json.load(f)

# Extract robot positions and cube names assigned manually
robot_points = data["robot_points"]   # should be a list of dicts with x,y coordinates
cube_names = data["cube_names"]       # list of strings like ["red1", "red2", "green1", ...]

# Optional: rotations for each position
rotations = [7, 0, 0, 8.576482772827148, -1.7244043350219727, 
             9.979423522949219, 0.07942359894514084, -9.132341384887695]

# Add rotation to robot points
for i, p in enumerate(robot_points):
    p["r"] = rotations[i] if i < len(rotations) else 0
    p["name"] = cube_names[i]  # assign name from OpenCV calibration

# Dobot setup
device = Dobot(port="/dev/ttyUSB0")

# Constants
SAFE_Z = 35
PICK_Z = -42.50025939941406
Center_x = 245
Center_y = 0
place_z_levels = [-42.02153778076172, -17.51886749267578, 6.19256591796875, 32.11168670654297]

# Track stacking and last Z
stack_counter = 0
last_z = PICK_Z + SAFE_Z

# Pick & Place function
def pick_and_place(cube_name):
    global stack_counter, last_z
    if stack_counter >= len(place_z_levels):
        messagebox.showinfo("Stack Full", "All stack levels are already used!")
        return

    pos = next((p for p in robot_points if p["name"] == cube_name), None)
    if pos is None:
        messagebox.showerror("Error", f"No robot position found for {cube_name}")
        return

    current_z = place_z_levels[stack_counter]

    try:
        # Step 1: Hover above cube
        device.move_to(x=pos["x"], y=pos["y"], z=last_z, r=pos["r"])

        # Step 2: Move down to pick
        device.move_to(x=pos["x"], y=pos["y"], z=PICK_Z, r=pos["r"])
        device.suck(True)
        time.sleep(1)

        # Step 3: Lift to stack height + SAFE_Z
        device.move_to(x=pos["x"], y=pos["y"], z=current_z + SAFE_Z, r=pos["r"])

        # Step 4: Move horizontally to center
        device.move_to(x=Center_x, y=Center_y, z=current_z + SAFE_Z, r=pos["r"])

        # Step 5: Place cube
        device.move_to(x=Center_x, y=Center_y, z=current_z, r=pos["r"])
        time.sleep(1)
        device.suck(False)
        time.sleep(1)

        # Step 6: Lift after placing
        device.move_to(x=Center_x, y=Center_y, z=current_z + SAFE_Z, r=pos["r"])

        # Update stack and last_z
        stack_counter += 1
        last_z = current_z + SAFE_Z
        print(f"{cube_name} placed at stack level {stack_counter}, next hover Z = {last_z}")

    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", str(e))

# GUI
root = tk.Tk()
root.title("Dobot Pick-and-Place (From Camera Calibration)")

tk.Label(root, text="Select a cube to pick & stack:").pack(pady=5)

# Buttons for each cube from camera calibration
for cube in robot_points:
    btn = tk.Button(root, text=cube["name"], width=30,
                    command=lambda name=cube["name"]: pick_and_place(name))
    btn.pack(pady=3)

# Quit button
btn_quit = tk.Button(root, text="Quit", width=30, command=lambda: (device.close(), root.destroy()))
btn_quit.pack(pady=10)

root.mainloop()
