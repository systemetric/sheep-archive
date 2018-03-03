from sr.robot import Robot
import time

multiplier_left = 1
multiplier_right = 0.92

distance_mps = 1.0 / 6.4
angle_dps = 360.0 / 8.5

R = Robot()
def move(distance):
    R.motors[0].m0.power = multiplier_left * 30
    R.motors[0].m1.power = multiplier_right * -30
    time.sleep(distance / distance_mps)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(degrees):
    R.motors[0].m0.power = multiplier_left * 30
    R.motors[0].m1.power = multiplier_right * 30
    time.sleep(degrees / angle_dps)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
