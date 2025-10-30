import tkinter as tk
from tkinter import messagebox, ttk
from pydobot import Dobot
import time
import json

# Load calibrated JSON from OpenCV calibration
with open("caliberated", "r") as f:
    data = json.load(f)

robot_points = data["robot_points"]  # list of dicts with x,y
cube_names = data["cube_names"]      # list of strings like ["red1","red2","green1", ...]

# Optional: rotations for each position
rotations = [7, 0, 0, 8.576482772827148, -1.7244043350219727,
             9.979423522949219, 0.07942359894514084, -9.132341384887695]

# Assign names and rotations
for i, p in enumerate(robot_points):
    p["r"] = rotations[i] if i < len(rotations) else 0
    p["name"] = cube_names[i]

# Dobot setup
device = Dobot(port="/dev/ttyUSB0")

# Constants
SAFE_Z = 35
PICK_Z = -47.50025939941406
Center_x = 245
Center_y = 0
Z_ERROR = 6
place_z_levels = [-42.02153778076172-Z_ERROR, -17.51886749267578-Z_ERROR, 6.19256591796875-Z_ERROR, 32.11168670654297-Z_ERROR]

# Home (custom center) position
HOME_X = 245.00001525878906
HOME_Y = 0.0
HOME_Z = 120
HOME_R = 0.07942359894514084

# Track stacking and last Z
stack_counter = 0
last_z = PICK_Z + SAFE_Z

# Track selected cubes (full names)
selected_cubes = []

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
        device.move_to(x=pos["x"], y=pos["y"], z=last_z, r=pos["r"])
        device.move_to(x=pos["x"], y=pos["y"], z=PICK_Z, r=pos["r"])
        device.suck(True)
        time.sleep(1)

        device.move_to(x=pos["x"], y=pos["y"], z=current_z + SAFE_Z, r=pos["r"])
        device.move_to(x=Center_x, y=Center_y, z=current_z + SAFE_Z, r=pos["r"])
        device.move_to(x=Center_x, y=Center_y, z=current_z, r=pos["r"])
        time.sleep(1)
        device.suck(False)
        time.sleep(1)
        device.move_to(x=Center_x, y=Center_y, z=current_z + SAFE_Z, r=pos["r"])

        stack_counter += 1
        last_z = current_z + SAFE_Z
        print(f"{cube_name} placed at stack level {stack_counter}, next hover Z = {last_z}")

    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", str(e))

# Start stacking based on selected cubes
def start_stacking():
    if not selected_cubes:
        messagebox.showwarning("Warning", "No cubes selected!")
        return

    for cube_name in selected_cubes:
        pick_and_place(cube_name)

# Move Dobot to custom Home Position
def move_home():
    try:
        device.move_to(x=HOME_X, y=HOME_Y, z=HOME_Z, r=HOME_R)
        print(f"Moved to Home position: x={HOME_X}, y={HOME_Y}, z={HOME_Z}, r={HOME_R}")
    except Exception as e:
        print("Error moving home:", e)
        messagebox.showerror("Error", str(e))

# Reset Dobot using its built-in homing
def reset_dobot():
    try:
        device.home()
        print("Dobot homing executed.")
    except Exception as e:
        print("Error during reset/home:", e)
        messagebox.showerror("Error", str(e))

# GUI for selecting 4 cubes (full names)
root = tk.Tk()
root.title("Select 4 Cubes to Stack")

tk.Label(root, text="Select 4 cubes (exact names) to stack:").pack(pady=5)

# Create 4 dropdowns
cube_vars = [tk.StringVar(value=cube_names[0]) for _ in range(4)]
for i in range(4):
    dropdown = ttk.Combobox(root, values=cube_names, textvariable=cube_vars[i], state="readonly")
    dropdown.pack(pady=3)

def save_cubes_and_start():
    global selected_cubes
    selected_cubes = [var.get() for var in cube_vars]
    print("Selected cubes:", selected_cubes)
    start_stacking()

btn_start = tk.Button(root, text="Start Stacking", command=save_cubes_and_start)
btn_start.pack(pady=10)

btn_home = tk.Button(root, text="Home (Move to Position)", command=move_home)
btn_home.pack(pady=5)

btn_reset = tk.Button(root, text="Reset (device.home)", command=reset_dobot)
btn_reset.pack(pady=5)

btn_quit = tk.Button(root, text="Quit", command=lambda: (device.close(), root.destroy()))
btn_quit.pack(pady=5)

root.mainloop()
