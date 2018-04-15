# encoding: utf-8

# Moving to resolution change
# Navigating back from walls

from __future__ import print_function

import nicerobot
import time
import threading
import operator

# Initialise robot
print("🤖 Initialising robot...")
R = nicerobot.Robot()
print("🔋 Battery: {}V".format(R.battery_level()))


def timer():
    mins = 0.0
    while True:
        time.sleep(30)
        mins += 0.5
        print(
            " ______________________\n(0RGSDOFCJftli;:.:. .  )\n T\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"T\n |.;....,..........;..|\n |;;:: .  .    .      |\n l;;;:. :   .     ..  ;\n `;;:::.: .    .     .\'\n  l;;:. ..  .     .: ;\n  `;;::.. .    .  ; .\'\n   l;;:: .  .    \/  ;\n    \\;;:. .   .,\'  \/\n     `\\;:.. ..\'  .\'\n       `\\;:.. ..\'\n         \\;:. \/\n          l; f\n          `;f\'\n           ||\n           ;l.\n          ;: l\n         \/ ;  \\\n       ,\/  :   `.\n     .\/\' . :     `.\n    \/\' ,\'  :       \\\n   f  \/  . :        i\n  ,\' ;  .  :        `.\n  f ;  .   :      .  i\n .\'    :   :       . `.\n f ,  .    ;       :  i\n |    :  ,\/`.       : |\n |    ;,\/;:. `.     . |\n |___,\/;;:. . .`._____|\n(QB0ZDOLC7itz!;:.:. .  )\n \"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"")
        print("⏲️ {} mins".format(mins))


timer_thread = threading.Thread(target=timer)
timer_thread.start()

led_pattern = [(0, 255, 0), (0, 0, 0), (255, 255, 255)]
led_pattern_index = 0


def set_led_pattern(pattern):
    global led_pattern
    global led_pattern_index
    led_pattern = pattern
    led_pattern_index = 0


def do_led_pattern():
    global led_pattern_index
    while True:
        print("Setting LED to {}".format(led_pattern[led_pattern_index]))
        R.motors[0].led.colour = led_pattern[led_pattern_index]
        led_pattern_index += 1
        if led_pattern_index >= len(led_pattern):
            led_pattern_index = 0
        time.sleep(1)


led_thread = threading.Thread(target=do_led_pattern)
# led_thread.start()

# Zone stuff
# noinspection PyUnresolvedReferences
zone = R.zone  # R.zone  # R.zone  # 3
print("🗺️ Robot is in Zone {}".format(zone))
# Marker ranges:
#   Arena Boundary: (0 - 23)
#   Tokens:         (32 - 71)
#   Bucket side:    (72 - 75)
#   Bucket end:     (76 - 79)
quadrants = [
    [72, 76, 0, 23, 1, 22, 2, 21],
    [73, 77, 6, 5, 7, 4, 8, 3],
    [74, 78, 12, 11, 13, 10, 14, 9],
    [75, 79, 18, 17, 19, 16, 20, 15]
]
third_markers = [2, 3, 8, 9, 14, 15, 20, 21]
sorted_quadrants = [
    quadrants[zone],
    quadrants[(zone - 1) % 4],
    quadrants[(zone + 1) % 4],
    quadrants[(zone + 2) % 4]
]
relative_quadrants = [
    quadrants[zone],
    quadrants[(zone + 1) % 4],
    quadrants[(zone + 2) % 4],
    quadrants[(zone + 3) % 4]
]
zones = [
    [0, 1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10, 11],
    [12, 13, 14, 15, 16, 17],
    [18, 19, 20, 21, 22, 23]
]
sorted_zones = [
    zones[zone],
    zones[(zone - 1) % 4],
    zones[(zone + 1) % 4],
    zones[(zone + 2) % 4]
]
relative_zones = [
    zones[zone],
    zones[(zone + 1) % 4],
    zones[(zone + 2) % 4],
    zones[(zone + 3) % 4]
]
sides = [72, 73, 74, 75]
other_buckets = []
for i in range(1, len(sorted_quadrants)):
    for code in sorted_quadrants[i]:
        if code >= 72:
            other_buckets.append(code)


# Gets the index of the quadrant that a marker is in, where 0 is the home and 3 is the opposite


def sorted_quadrant_index(m):
    for quadrant_index in range(len(sorted_quadrants)):
        if m.info.code in sorted_quadrants[quadrant_index]:
            return quadrant_index
    return 5  # An impossible quadrant


def sorted_zone_index(m):
    for zone_index in range(len(sorted_zones)):
        if m.info.code in sorted_zones[zone_index]:
            return zone_index
    return 5  # An impossible zone


def relative_quadrant_index(m):
    for quadrant_index in range(len(relative_quadrants)):
        if m.info.code in relative_quadrants[quadrant_index]:
            return quadrant_index
    return 5  # An impossible quadrant


def relative_zone_index(m):
    for zone_index in range(len(relative_zones)):
        if m.info.code in relative_zones[zone_index]:
            return zone_index
    return 5  # An impossible zone


# Move out of start area
print("⬆️ Moving out of start area...")
time.sleep(1)
R.move(0.5)
# time.sleep(0.2)
# R.move(-0.25)
time.sleep(1)

# Store of already collected cubes
collected_cube_codes = []

anitclockwise_markers = []
anitclockwise_markers.extend(relative_zones[3])
anitclockwise_markers.extend(relative_zones[2])

pickup_index = 1
clockwise = False
while True:
    print("\n\n--- Cube {} ---".format(pickup_index))
    pickup_index += 1

    # Pickup cube
    target_cube_code = 0
    cube_pickup_tries = 0
    while True:
        # Find a cube
        print("📦 Looking for cubes...")
        new_cubes, found_res = R.look_for([nicerobot.TOKEN], collected_cube_codes, sorted_quadrant_index,
                                          resolution=(1920, 1088) if len(collected_cube_codes) >= 2 else (640, 480))
        # new_cubes = [cube for cube in cubes if not(cube.info.code in collected_cube_codes)]
        print("  Found {} cube(s)".format(len(new_cubes)))
        if len(new_cubes) == 0:
            # No new cubes found, so move a bit
            print("  ❌ No new cubes were found, so moving a bit before looking again")
            R.turn(90)
            R.move(1)
        else:
            # Calculate nearest cube
            print("Working out closest cube..")
            new_cubes.sort(key=operator.attrgetter('dist'))
            print("PRINTING SORTED CUBES!!!")
            for new_cube in new_cubes:
                print(new_cube.dist)
            print("FINISHED PRINTING SORTED CUBES!!!")

            target_cube_code = new_cubes[0].info.code
            print("⬆️ Moving towards cube {} which is {}m off the ground...".format(target_cube_code,
                                                                                    new_cubes[0].centre.world.y))
            if not (R.move_to(target_cube_code, found_res)):
                # We lost the cube so try and find another
                print("  ⚠️ Cannot see the cube anymore so looking for a new one")
                continue

            # Try and pick it up
            print("🏗️ Trying to pick up the cube...")
            R.pickup_cube()

            # Check if it was picked up
            print("  👀 Checking if the cube was picked up...")
            R.move(-0.5, speed=50)
            cubes = R.see()
            same_cubes = [
                cube for cube in cubes if cube.info.code == target_cube_code]
            if len(same_cubes) == 0:
                # We can't see the cube in front of us so we must be holding it
                print("    ✔️ Cannot see the cube, so assuming it was")
                R.turn(90 if clockwise else -90)
                break

            # Otherwise try and pick it up again
            print("    ⚠️ Seen the cube, so turning off the pump, and trying again...")
            R.drop()

    already_found_wall = False
    use_higher_resolution = False
    # Goto the bucket and drop the cube
    while True:
        # Find buckets or walls
        print("\n🚩 Looking for buckets and walls...")
        types = [nicerobot.BUCKET, nicerobot.TOKEN]
        if not already_found_wall:
            types.append(nicerobot.WALL)
        ignored = []
        ignored.extend(other_buckets)
        for potential_marker in range(32, 72):
            if potential_marker != target_cube_code:
                ignored.append(potential_marker)
        markers, found_res = R.look_for(types, ignored, sorted_quadrant_index, resolution=(1920, 1088),
                                        clockwise=clockwise)  # if not already_found_wall else (640, 480))
        if len(markers) == 0:
            # No relevant markers found, so move a bit
            print(
                "  ❌ No relevant markers were found, so moving a bit before looking again")
            already_found_wall = False
            R.turn(90)
            R.move(1)
        else:
            # Sort the seen markers
            print("📜 Sorting the markers...")
            markers.sort(key=sorted_quadrant_index)
            buckets = []
            walls = []
            aborted = False
            for marker in markers:
                if marker.info.marker_type == nicerobot.MARKER_ARENA:
                    walls.append(marker)
                elif marker.info.marker_type == nicerobot.MARKER_TOKEN:
                    if marker.info.code == target_cube_code:
                        print("☢️☢️☢️ ABORT!!!!!! CUBE WHICH IS APPARENTLY PICKED UP WAS SEEN!!!! ☢️☢️☢️")
                        pickup_index -= 1
                        R.drop()
                        aborted = True
                        break
                else:
                    buckets.append(marker)
            if aborted:
                break
                # Check for buckets first
            print("🗑️ Checking for buckets...")
            if len(buckets) > 0:
                buckets.sort(key=operator.attrgetter('rot_y'), reverse=True)
                # Get the target bucket as the 1st one
                target_bucket = buckets[0]
                # Find the quadrant the bucket is in
                target_bucket_quadrant = sorted_quadrant_index(target_bucket)
                print("🗺️ Target bucket {} is in quadrant {}".format(
                    target_bucket.info.code, target_bucket_quadrant))
                # Try to move towards the bucket
                print("⬆️ Moving towards bucket {}...".format(
                    target_bucket.info.code))
                if not (R.move_to(target_bucket.info.code, found_res)):
                    # We lost the bucket so try and find another
                    print("  ⚠️ Cannot see the bucket anymore so looking for a new one")
                    continue

                # Check if side
                is_side = target_bucket.info.code in sides

                # We reached the bucket so drop/shake the cube off
                print("🏗️ Dropping the cube...")
                R.drop()
                time.sleep(0.1)
                # print("  🎵 Shake it off, shake it off 🎵")
                # R.turn(-10)
                # R.turn(20)
                # R.turn(-20)
                # R.turn(10)
                # time.sleep(0.1)

                # Register that we collected this cube
                print("📝 Registering cube {} as collected...".format(
                    target_cube_code))
                collected_cube_codes.append(target_cube_code)
                print("📦 The following cubes have now been collected:")
                for cube_code in collected_cube_codes:
                    print("  - {}".format(cube_code))

                # Reverse out and rotate
                print("🔄 Reversing out and rotating...")
                R.move(-0.4)
                print("Is side:", is_side)
                R.turn(-120 if is_side else 120)
                clockwise = not is_side
                time.sleep(0.1)
                R.move(0.3)

                # Then go and look for another cube
                break

            # Otherwise check for and move towards walls
            print("⬜ No buckets found, so checking for walls...")
            if len(walls) > 0:
                # Get the target wall as the 1st one
                target_wall = walls[0]
                # Find the quadrant the wall is in
                target_wall_quadrant = sorted_quadrant_index(target_wall)
                target_wall_zone = relative_zone_index(target_wall)
                print("🗺️ Target wall {} is in quadrant {}".format(
                    target_wall.info.code, target_wall_quadrant))
                # If it's our home...
                if target_wall_quadrant == 0:
                    clockwise = not (walls[0].info.code in anitclockwise_markers)
                    print("Clockwise:", clockwise)

                    if target_wall.info.code in third_markers:
                        R.turn(30 if clockwise else -30)
                        if target_wall.dist > 1.5:
                            R.move(0.3)
                    else:
                        # Try to move towards the bucket
                        print("⬆️ Moving towards wall {}...".format(
                            walls[0].info.code))
                        if not (R.move_to(walls[0].info.code, found_res)):
                            R.turn(30 if clockwise else -30)

                        already_found_wall = True
                # Otherwise try and turn to face home
                elif target_wall_zone == 0:
                    print("↩️ Turning clockwise a little to face home...")
                    clockwise = True
                    R.turn(45)
                elif target_wall_zone == 1:
                    print("↩️ Turning clockwise a lot to face home...")
                    clockwise = True
                    R.turn(90)
                elif target_wall_zone == 2:
                    print("↩️ Turning anticlockwise a lot to face home...")
                    clockwise = False
                    R.turn(-90)
                elif target_wall_zone == 3:
                    print("↩️ Turning anticlockwise a little to face home...")
                    clockwise = False
                    R.turn(-45)
                continue

    # clockwise = False

    if pickup_index == 3:
        print("SWITCHING RES!!!!!!!")
        print("SWITCHING RES!!!!!!!")
        print("SWITCHING RES!!!!!!!")
        R.start_res = (1296, 976)
