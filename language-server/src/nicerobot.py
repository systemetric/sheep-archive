import time

from sr.robot import *

R = Robot()

SERVO_ARM = 0
SERVO_LEFT = 2
SERVO_RIGHT = 1

GPIO_GATE = 1
GPIO_PUMP = 2

MULTIPLIER_LEFT = -1
MULTIPLIER_RIGHT = 0.95  # 0.91

SPEED_50 = 1.25 / 3
SPEED_100 = 1.7 * SPEED_50 * 1.25
SPEED_ANGULAR_30 = 360 / 4.25

markers = []

R.gpio.pin_mode(GPIO_GATE, OUTPUT)
R.gpio.pin_mode(GPIO_PUMP, OUTPUT)
R.gpio.digital_write(GPIO_GATE, True)
R.servos[SERVO_RIGHT] = 0
R.servos[SERVO_LEFT] = 0

# Consts for find()
BUCKET = 0
CUBE = 1


def move(distance):
    pass


def turn(angle):
    pass


def pickup_cube():
    pass


def succ():
    pass


def pump_on():
    pass


def drop():
    pass


def find(thing):
    pass
