import random
import nicerobot
import time

R = nicerobot.Robot()

while True:
    dist = random.random() * 3
    print "Dist:", dist
    angle = random.randrange(0, 360)
    print "Angel:", angle

    R.move(dist)
    R.turn(angle)
    if random.random() > 0.5:
        R.succ()
        print "Succ"
    else:
        R.drop()
        print "Drop"

    R.motors[0].led.colour = (random.randrange(
        0, 255), random.randrange(0, 255), random.randrange(0, 255))

    t = random.random() * 3
    time.sleep(t)
    print "Time:", t
