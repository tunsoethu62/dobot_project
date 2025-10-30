import tkinter as tk
from tkinter import messagebox
from pydobot import Dobot
import time
import json

# Load your JSON mapping from calibration
with open("calibrated", "r") as f:
    data = json.load(f)

# Dobot setup
device = Dobot(port="/dev/ttyUSB0")

# Constants
SAFE_Z = 35
PICK_Z = -42.50025939941406
Center_x = 245
Center_y = 0

# Predefined positions (from JSON)
dobot_positions = data["robot_points"]      # x, y coords
cube_names = data["cube_names"]             # cube names assigned to positions

# Optional rotations (if you want strict r values)
rotations = [7,0,0,8.576482772827148,-1.7244043350219727,9.979423522949219,0.07942359894514084,-9.132341384887695]

# Combine positions with rotations and names
positions = []
for i, pos in enumerate(dobot_positions):
    positions.append({
        "name": cube_names[i],  # Use cube name
        "x": pos["x"],
        "y": pos["y"],
        "z": PICK_Z,
        "r": rotations[i] if i < len(rotations) else 0
    })

# Stacking Z levels at center
place_z_levels = [-42.02153778076172, -17.51886749267578, 6.19256591796875, 32.11168670654297]
stack_counter = 0  # Track how many cubes have been placed

# Track last Z hover for next pick
last_z = PICK_Z + SAFE_Z  # initially hover above first pick

def pick_and_place(pos_idx):
    global stack_counter, last_z
    if stack_counter >= len(place_z_levels):
        messagebox.showinfo("Stack Full", "All stack levels are already used!")
        return

    pos = positions[pos_idx]
    current_z = place_z_levels[stack_counter]

    try:
        # Step 1: Hover above cube using last_z
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

        # Update stack and last_z for next pick
        stack_counter += 1
        last_z = current_z + SAFE_Z  # new hover height for next pick
        print(f"{pos['name']} placed at stack level {stack_counter}, next hover Z = {last_z}")

    except Exception as e:
        print("Error:", e)
        messagebox.showerror("Error", str(e))

# GUI
root = tk.Tk()
root.title("Dobot Pick-and-Place GUI (Cube Name Assignment)")

tk.Label(root, text="Select a cube to pick & stack:").pack(pady=5)

for i, pos in enumerate(positions):
    btn = tk.Button(root, text=pos["name"], width=30, command=lambda idx=i: pick_and_place(idx))
    btn.pack(pady=3)

btn_quit = tk.Button(root, text="Quit", width=30, command=lambda: (device.close(), root.destroy()))
btn_quit.pack(pady=10)

root.mainloop()
