from sr.robot import Robot
import time

multiplier_left = 1
multiplier_right = 0.92

distance_mps = 1.0 / 6.4
angle_dps = 360.0 / 8.5

R = Robot()
def move(distance):
    multiplier = 1
    if distance < 0:
        multiplier = -1
    R.motors[0].m0.power = multiplier_left * 30 * multiplier
    R.motors[0].m1.power = multiplier_right * -30 * multiplier
    time.sleep(abs(distance / distance_mps))
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(degrees):
    multiplier = 1
    if degrees < 0:
        multiplier = -1
    R.motors[0].m0.power = multiplier_left * 30 * multiplier
    R.motors[0].m1.power = multiplier_right * 30 * multiplier
    time.sleep(abs(degrees / angle_dps))
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
