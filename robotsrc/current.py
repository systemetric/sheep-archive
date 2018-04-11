# encoding: utf-8

# Jittering wheels (perhaps battery)
# Valve
# If every sees cube apparently holding, then abort, and start again

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
        print("⏲️ {} mins".format(mins))


timer_thread = threading.Thread(target=timer)
timer_thread.start()

# Zone stuff
# noinspection PyUnresolvedReferences
zone = 3  # R.__zone
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
sorted_quadrants = [
    quadrants[zone],
    quadrants[(zone - 1) % 4],
    quadrants[(zone + 1) % 4],
    quadrants[(zone + 2) % 4]
]
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


# Move out of start area
print("⬆️ Moving out of start area...")
time.sleep(1)
R.move(0.5)
time.sleep(1)

# Store of already collected cubes
collected_cube_codes = []

# TODO: Replace with while True during competition
for i in range(6):
    print("\n\n--- Cube {} ---".format(i))

    # Pickup cube
    target_cube_code = 0
    cube_pickup_tries = 0
    while True:
        # Find a cube
        print("📦 Looking for cubes...")
        new_cubes = R.look_for([nicerobot.TOKEN], collected_cube_codes, sorted_quadrant_index, resolution=(1920, 1088) if len(collected_cube_codes) >= 2 else (640, 480))
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

            target_cube_code = new_cubes[0].info.code
            print("⬆️ Moving towards cube {}...".format(target_cube_code))
            if not(R.move_to(target_cube_code)):
                # We lost the cube so try and find another
                print("  ⚠️ Cannot see the cube anymore so looking for a new one")
                continue

            # Try and pick it up
            print("🏗️ Trying to pick up the cube...")
            R.pickup_cube()

            # Check if it was picked up
            print("  👀 Checking if the cube was picked up...")
            R.move(-0.5)
            cubes = R.see()
            same_cubes = [
                cube for cube in cubes if cube.info.code == target_cube_code]
            if len(same_cubes) == 0:
                # We can't see the cube in front of us so we must be holding it
                print("    ✔️ Cannot see the cube, so assuming it was")
                break

            # Otherwise try and pick it up again
            print("    ⚠️ Seen the cube, so turning off the pump, and trying again...")
            R.drop()

    already_found_wall = False
    # Goto the bucket and drop the cube
    while True:
        # Find buckets or walls
        print("\n🚩 Looking for buckets and walls...")
        types = [nicerobot.BUCKET]
        if not already_found_wall:
            types.append(nicerobot.WALL)
        markers = R.look_for(types, other_buckets, sorted_quadrant_index, resolution=(1920, 1088)) # if not already_found_wall else (640, 480))
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
            for marker in markers:
                if marker.info.marker_type == nicerobot.MARKER_ARENA:
                    walls.append(marker)
                else:
                    buckets.append(marker)

            # Check for buckets first
            print("🗑️ Checking for buckets...")
            if len(buckets) > 0:
                # Get the target bucket as the 1st one
                target_bucket = buckets[0]
                # Find the quadrant the bucket is in
                target_bucket_quadrant = sorted_quadrant_index(target_bucket)
                print("🗺️ Target bucket {} is in quadrant {}".format(
                    target_bucket.info.code, target_bucket_quadrant))
                # Try to move towards the bucket
                print("⬆️ Moving towards bucket {}...".format(
                    target_bucket.info.code))
                if not(R.move_to(target_bucket.info.code)):
                    # We lost the bucket so try and find another
                    print("  ⚠️ Cannot see the bucket anymore so looking for a new one")
                    continue
                # We reached the bucket so drop/shake the cube off
                print("🏗️ Dropping the cube...")
                R.drop()
                time.sleep(0.1)
                print("  🎵 Shake it off, shake it off 🎵")
                R.turn(-10)
                R.turn(20)
                R.turn(-20)
                R.turn(10)
                time.sleep(0.1)

                # Register that we collected this cube
                print("📝 Registering cube {} as collected...".format(
                    target_cube_code))
                collected_cube_codes.append(target_cube_code)
                print("📦 The following cubes have now been collected:")
                for cube_code in collected_cube_codes:
                    print("  - {}".format(cube_code))

                # Then go and look for another cube
                break

            # Otherwise check for and move towards walls
            print("⬜ No buckets found, so checking for walls...")
            if len(walls) > 0:
                # Get the target wall as the 1st one
                target_wall = walls[0]
                # Find the quadrant the wall is in
                target_wall_quadrant = sorted_quadrant_index(target_wall)
                print("🗺️ Target wall {} is in quadrant {}".format(
                    target_wall.info.code, target_wall_quadrant))
                # If it's our home...
                if target_wall_quadrant == 0:
                    # Try to move towards the bucket
                    print("⬆️ Moving towards wall {}...".format(
                        walls[0].info.code))
                    if not(R.move_to(walls[0].info.code)):
                        R.turn(30)
                    already_found_wall = True
                # Otherwise try and turn to face home
                elif target_wall_quadrant == 1:
                    print("↪️ Turning anticlockwise to face home...")
                    R.turn(-60)
                elif target_wall_quadrant == 2:
                    print("↩️ Turning clockwise to face home...")
                    R.turn(60)
                elif target_wall_quadrant == 3:
                    print("🔄 Changing direction to face home...")
                    R.turn(180)
                continue

    # Reverse out and rotate
    print("🔄 Reversing out and rotating...")
    R.move(-0.4)
    R.turn(180)
