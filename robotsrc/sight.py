from __future__ import print_function

import nicerobot
import time

R = nicerobot.Robot()

while True:
    markers = R.see()
    print("----------------------------")
    for marker in markers:
        print("Marker {}: {}m away, {} degrees".format(marker.info.code, marker.dist, marker.rot_y))
    print("----------------------------")
    time.sleep(1)
