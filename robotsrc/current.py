# encoding: utf-8

from __future__ import print_function

import nicerobot
import time

# Initialise robot
print("🤖 Initialising robot...")
R = nicerobot.Robot()

# Move out of start area
print("⬆️ Moving out of start area...")
time.sleep(1)
R.move(0.5)
time.sleep(1)

# Store of already collected cubes
collected_cube_codes = []

# TODO: Replace with while True during competition
for i in range(3):
    print("--- Cube {} ---".format(i))

    # Pickup cube
    target_cube_code = 0
    while True:
        # Find a cube
        print("📦 Looking for cubes...")
        cubes = R.look_for([nicerobot.TOKEN])
        new_cubes = [cube for cube in cubes if not(cube.info.code in collected_cube_codes)]
        print("  Found {} cube(s), of which {} are new".format(len(cubes), len(new_cubes)))
        if len(new_cubes) == 0:
            # No new cubes found, so move a bit
            print("  🚫 No new cubes were found, so moving a bit before looking again")
            R.turn(90)
            R.move(1)
        else:
            # Goto the 1st cube
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
            same_cubes = [cube for cube in cubes if cube.info.code == target_cube_code]
            if len(same_cubes) == 0:
                # We can't see the cube in front of us so we must be holding it
                print("    ✔️ Cannot see the cube, so assuming it was")
                break

            # Otherwise try and pick it up again
            print("    ⚠️ Seen the cube, so turning off the pump, and trying again...")
            R.drop()

    # Goto the bucket and drop the cube
    while True:
        # Find buckets or walls
        print("🚩 Looking for buckets and walls...")
        markers = R.look_for([nicerobot.BUCKET, nicerobot.WALL])
        if len(markers) == 0:
            # No relevant markers found, so move a bit
            print("  🚫 No relevant markers were found, so moving a bit before looking again")
            R.turn(90)
            R.move(1)
        else:
            # Sort the seen markers
            print("📜 Sorting the markers...")
            buckets = []
            walls = []
            for marker in markers:
                if marker.info.marker_type == nicerobot.MARKER_ARENA:
                    walls.append(marker)
                else:
                    buckets.append(marker)

            # Check for buckets first
            print("🕳️ Checking for buckets...")
            if len(buckets) > 0:
                # TODO: Decide which way to move depending on the bucket
                # Try to move towards the bucket
                print("⬆️ Moving towards bucket {}...".format(buckets[0].info.code))
                if not(R.move_to(buckets[0].info.code)):
                    # We lost the bucket so try and find another
                    print("  ⚠️ Cannot see the bucket anymore so looking for a new one")
                    continue

                # We reached the bucket so drop/shake the cube off
                print("🏗️ Dropping the cube...")
                R.drop()
                print("  🎵 <i>Shake it off, shake it off</i> 🎵")
                R.turn(-10)
                R.turn(20)
                R.turn(-10)

                # Register that we collected this cube
                print("📝 Registering cube {} as collected...".format(target_cube_code))
                collected_cube_codes.append(target_cube_code)
                print("📦 The following cubes have now been collected:")
                for cube_code in collected_cube_codes:
                    print("  - {}".format(cube_code))

                # Then go and look for another cube
                break

            # Otherwise check for and move towards walls
            print("⬜ No buckets found, so checking for walls...")
            if len(walls) > 0:
                # TODO: Decide which way to move depending on the wall
                print("⬆️ Moving towards wall {}...".format(walls[0].info.code))
                R.move_to(walls[0].info.code)

    # Reverse out and rotate
    print("🔄 Reversing out and rotating...")
    R.move(-0.4)
    R.turn(180)
