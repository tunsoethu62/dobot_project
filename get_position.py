from serial.tools import list_ports
from pydobot import Dobot
import time

device = Dobot (port = "/dev/ttyUSB0")


pose = device.get_pose()
print ("Current Pose:", pose)

device.close()