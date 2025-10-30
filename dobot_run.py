from serial.tools import list_ports
from pydobot import Dobot
import time

device = Dobot (port = "/dev/ttyUSB0")
SAFE_Z = 20
PICK_Z = -47.50025939941406
Center_x = 245
Center_y = 0

pose = device.get_pose()
print ("Current Pose:", pose)

#1st
device.move_to(x=280.3928527832031, y=-29.90688705444336, z=PICK_Z+ SAFE_Z, r=0)
device.move_to(x=280.3928527832031, y=-29.90688705444336, z=PICK_Z, r=0)
device.suck(True)
time.sleep(1)
device.move_to(x=280.3928527832031, y=-29.90688705444336, z=PICK_Z+35, r=0)
device.move_to(x=Center_x, y=Center_y, z=PICK_Z+35, r=6.617647171020508)
device.move_to(x=Center_x, y=Center_y, z=PICK_Z + 3, r=6.617647171020508)

time.sleep(1)
device.suck(False)
time.sleep(0.5)
device.move_to(x=Center_x, y=Center_y, z=PICK_Z+SAFE_Z, r=6.617647171020508)

#2nd

device.move_to(x=242.74148559570312, y=-33.28932571411133, z=PICK_Z + SAFE_Z, r=-1.7244043350219727)
device.move_to(x=242.74148559570312, y=-33.28932571411133, z=PICK_Z, r=-1.7244043350219727)
device.suck(True)
time.sleep(1)
device.move_to(x=242.74148559570312, y=-33.28932571411133, z=-21.33783721923828+SAFE_Z, r=-1.7244043350219727)

device.move_to(x=Center_x, y=Center_y, z=-21.33783721923828+SAFE_Z, r=7.358823299407959)
device.move_to(x=Center_x, y=Center_y, z=-21.33783721923828, r=7.358823299407959)
time.sleep(1)
device.suck(False)
time.sleep(0.7)
device.move_to(x=Center_x, y=Center_y, z=-21.33783721923828+SAFE_Z, r=7.358823299407959)

#3rd
device.move_to(x=209.5706024169922, y=-29.52985191345215, z=-21.33783721923828+SAFE_Z, r=7.358823299407959)
device.move_to(x=209.5706024169922, y=-29.52985191345215, z=PICK_Z, r=-1.1911768913269043)
device.suck(True)
time.sleep(1)
device.move_to(x=209.5706024169922, y=-29.52985191345215, z=3.0769500732421875+20, r=-1.7244043350219727)

device.move_to(x=Center_x, y=Center_y, z=3.0769500732421875+SAFE_Z, r=7.702940940856934)
device.move_to(x=Center_x, y=Center_y, z=3.0769500732421875, r=7.702940940856934)
time.sleep(1)
device.suck(False)
time.sleep(0.7)
device.move_to(x=Center_x, y=Center_y, z=3.0769500732421875+SAFE_Z, r=7.702940940856934)

#4th
device.move_to(x=204.14761352539062, y=6.510175704956055, z=3.0769500732421875+SAFE_Z, r=8.655881881713867)
device.move_to(x=204.14761352539062, y=6.510175704956055, z=PICK_Z, r=8.655881881713867)
device.suck(True)
time.sleep(1)
device.move_to(x=204.14761352539062, y=6.510175704956055, z=28.54210662841797+SAFE_Z, r=-1.7244043350219727)

device.move_to(x=Center_x, y=Center_y, z=28.54210662841797+SAFE_Z, r=7.702940940856934)
device.move_to(x=Center_x, y=Center_y, z=28.54210662841797, r=7.702940940856934)
time.sleep(1)
device.suck(False)
time.sleep(0.7)
device.move_to(x=Center_x, y=Center_y, z=28.54210662841797+20, r=7.702940940856934)

device.close()