from time import sleep
from pydobot import Dobot

device = Dobot(port="/dev/ttyUSB0")
sleep(2)  # wait for initialization
pose = device.get_pose()
print(pose)
