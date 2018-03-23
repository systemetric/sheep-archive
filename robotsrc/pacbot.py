import RPi.GPIO as GPIO			# using Rpi.GPIO module
import time			# import function sleep for delay

#
# START OF MOTOR CONSTANTS
#
# Multipliers for Power
multiplier_left = 1
multiplier_right = 1

# Speeds
# Distance m/s
distance_mps = 1.0 / 1.0
# Angular degrees/s
angle_dps = 360.0 / 2.0
#
# END OF MOTOR CONSTANTS
#

AN2 = 13				# set pwm2 pin on MD10-Hat
AN1 = 12				# set pwm1 pin on MD10-hat
DIG2 = 24				# set dir2 pin on MD10-Hat
DIG1 = 26				# set dir1 pin on MD10-Hat)

class CytronBoard(object):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)			# GPIO numbering
        GPIO.setwarnings(False)			# enable warning from GPIO
        GPIO.setup(AN2, GPIO.OUT)		# set pin as output
        GPIO.setup(AN1, GPIO.OUT)		# set pin as output
        GPIO.setup(DIG2, GPIO.OUT)		# set pin as output
        GPIO.setup(DIG1, GPIO.OUT)		# set pin as output
        
        time.sleep(1)				# delay for 1 seconds

        self.p1 = GPIO.PWM(AN1, 100)		# set pwm for M1
        self.p2 = GPIO.PWM(AN2, 100)		# set pwm for M2
         
    def m1(self, speed):
        if speed <= 0 :
            GPIO.output(DIG1, GPIO.LOW)          # set DIG1 as LOW, to control direction
            speed = -speed
        else :
            GPIO.output(DIG1, GPIO.HIGH)         # set DIG1 as HIGH, to control direction
        if speed > 100:
            speed = 100                          # make sure we dont over do it!
        self.p1.start (speed)
            
    def m2(self, speed):
        if speed <= 0 :
            GPIO.output(DIG2, GPIO.LOW)          # set DIG2 as LOW, to control direction
            speed = -speed
        else :
            GPIO.output(DIG2, GPIO.HIGH)         # set DIG2 as HIGH, to control direction
        if speed > 100:
            speed = 100                          # make sure we dont over do it!
        self.p2.start (speed)

print "Starting Up"
CB = CytronBoard()

def move(distance):
    multiplier = 1
    if distance < 0:
        multiplier = -1
    print "Going", distance
    CB.m1(multiplier_left * -100 * multiplier)
    CB.m2(multiplier_right * -100 * multiplier)
    time.sleep(abs(distance / distance_mps))
    print "Stopping move"
    CB.m1(0)
    CB.m2(0)

def turn(degrees):
    multiplier = 1
    if degrees < 0:
        multiplier = -1
    print "Turning", degrees
    CB.m1(multiplier_left * -100 * multiplier)
    CB.m2(multiplier_right * 100 * multiplier)
    print "Sleeping"
    time.sleep(abs(degrees / angle_dps))
    print "Stopping turning"
    CB.m1(0)
    CB.m2(0)