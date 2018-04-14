import random
import nicerobot
import time

R = nicerobot.Robot()

while True:
    R.move(random.randrange(0, 3, 0.1))
    R.turn(random.randrange(0, 360))
    if random.random() > 0.5:
        R.succ()
    else:
        R.drop()

    R.motors[0].led.colour = (random.randrange(
        0, 255), random.randrange(0, 255), random.randrange(0, 255))
    time.sleep(random.randrange(0, 3, 0.1))
