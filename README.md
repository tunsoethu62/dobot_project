# Dobot Cube Stacking — Camera Calibration & Stacking Controller

**Project:** Robot-assisted cube detection, calibration and stacking using OpenCV + Dobot (pydobot).  
**Author:** (Your name, e.g. Harry)  
**Last updated:** 2025-11-10

## Overview

This Python program uses a webcam to detect colored cubes, calibrates camera → Dobot workspace mapping (manual assignment of 8 reference cubes), and then controls a Dobot arm (via `pydobot`) to pick and stack selected cubes in the centre stacking area.

Key features:
- Color segmentation (HSV) to detect cubes and mark centroids.
- Manual calibration GUI to assign camera centroids to known Dobot coordinates.
- Linear mapping from camera (u,v) pixel coordinates → robot (x,y) coordinates.
- GUI for selecting cubes to stack and basic robot control (home, reset).
- Re-detection of newly placed cubes and automatic slot assignment.

---

## Requirements

- Hardware:
  - Dobot Magician (or compatible Dobot) with USB serial connection.
  - Webcam (USB camera). Adjust `camera_index` if needed.
- OS: Linux/macOS/Windows (the serial port path differs per OS)
- Python 3.8+ recommended

- Python packages:
  - `opencv-python` (`cv2`)
  - `numpy`
  - `pydobot`
  - `tkinter` (usually bundled with Python; on some Linux you need `python3-tk`)
  - (Optional) `pyserial` — often installed as dependency of `pydobot`

Install with pip:
```bash
pip install opencv-python numpy pydobot
# On Debian/Ubuntu if tkinter missing:
sudo apt install python3-tk
