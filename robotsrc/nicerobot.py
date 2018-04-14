# encoding: utf-8

from __future__ import division, print_function

import time
import weakref
import math

import sr.robot
from sr.robot import (
    INPUT, OUTPUT, INPUT_ANALOG, INPUT_PULLUP,
    MARKER_ARENA, MARKER_TOKEN, MARKER_BUCKET_SIDE, MARKER_BUCKET_END
)

__all__ = [
    # Our public API
    "Robot",
    "TOKEN", "BUCKET",
    # SR's API
    "MARKER_ARENA", "MARKER_TOKEN", "MARKER_BUCKET_SIDE", "MARKER_BUCKET_END",
    "INPUT", "OUTPUT", "INPUT_ANALOG", "INPUT_PULLUP",
]

TOKEN = object()
BUCKET = object()
WALL = object()


def __noop__(arg):
    raise RuntimeError("You called NOOP you fool!")


def _make_servo_property(servo_num, docstring=None):
    def getter(self):
        return self.servos[servo_num]

    def setter(self, value):
        if not (-160 <= value <= 160):
            raise ValueError(
                "Servo power must be in the range -160 to 160 (given: {})".format(value))
        self.servos[servo_num] = value

    return property(getter, setter, doc=docstring)


class GPIO(object):
    """A GPIO pin.

    Arguments:
        pin: A GPIO pin number that this object will represent.
        gpio: A `BlackJackBoardGPIO` instance to delegate to.

    Attributes:
        analog: The analog value of the pin.
        digital: The digital value of the pin.
        mode: The pin mode. This attribute is write-only.

    Notes:
        If a pin is accessed in the incorrect way (for example,
        configured as an output, then read), the result is undefined.
        It's possible that an `IOError` will be raised, or you may get
        an incorrect result, or demons may fly out of your nose.

    Examples:
        >>> R.pin_in.mode = INPUT
        >>> digital_value = R.pin_in.digital

        >>> R.pin_in_analog.mode = INPUT_ANALOG
        >>> analog_value = R.pin_in.analog
    """

    def __init__(self, pin, gpio):
        super(GPIO, self).__init__()
        self._pin = pin
        self._gpio = gpio

    @property
    def analog(self):
        return self._gpio.analog_read(self._pin)

    @property
    def digital(self):
        return self._gpio.digital_read(self._pin)

    @digital.setter
    def digital(self, value):
        self._gpio.digital_write(self._pin, value)

    def _set_mode(self, mode):
        self._gpio.pin_mode(self._pin, mode)

    mode = property(None, _set_mode)


class GPIOProperty(object):
    """An object representing a GPIO pin.

    This is a descriptor; it should usually be assigned to a class
    variable.

    Arguments:
        pin: A GPIO pin number, as for `GPIO`.
        gpio_attr: The name of the attribute on the class where a
            `BlackJackBoardGPIO` object is (or will be) available.
    """

    def __init__(self, pin):
        self._pin = pin
        self._gpio_cache = weakref.WeakKeyDictionary()

    # `self`: an instance of the descriptor;
    # `instance`: the instance the descriptor was accessed from, or None;
    # `owner`: the class the descriptor was accessed from.
    def __get__(self, instance, owner):
        if instance is None:
            return self  # Following the lead of `property`
        return self._get_gpio(instance)

    def __set__(self, instance, value):
        # Support setting outputs via e.g. `self.pin_out = True` rather
        # than having to go through `GPIO.digital`.
        assert instance is not None
        gpio = self._get_gpio(instance)
        gpio.digital = value

    def _get_gpio(self, instance):
        # We have to be quite careful to avoid potential races here.
        # Weak references are awesome, but can lead to subtle bugs.
        try:
            gpio = self._gpio_cache[instance]
        except KeyError:
            gpio = GPIO(self._pin, instance.gpio)
            self._gpio_cache[instance] = gpio
        return gpio


class Robot(sr.robot.Robot):
    # Servo number constants
    SERVO_ARM = 0
    SERVO_LEFT = 2
    SERVO_RIGHT = 1

    GPIO_GATE = 1
    GPIO_PUMP = 2

    ARM_UP = -160
    ARM_DOWN = 100

    MULTIPLIER_LEFT = -1
    MULTIPLIER_RIGHT = 0.9  # 0.88

    SPEED_50 = 3.6 / 10  # 1.25 / 3
    # SPEED_100 = 1.7 * SPEED_50 * 1.25
    SPEED_ANGULAR_30 = 90.0 / 1.3  # 360.0 / 4.25

    def __init__(self):
        super(Robot, self).__init__()

        if self.battery_level() < 11.0:
            print('╔══════════════════════╗')
            print('║╔════════════════════╗╚╗')
            print('║║████░░░░░░░░░░░░░░░░╚╗╚╗')
            print('║║████░░░Low Battery░░░║ ║')
            print('║║████░░░░░░░░░░░░░░░░╔╝╔╝')
            print('║╚════════════════════╝╔╝')
            print('╚══════════════════════╝')

        self.gate.mode = OUTPUT
        self.pump.mode = OUTPUT
        self.gate = True
        self.right_wheel = 0
        self.left_wheel = 0
        self.arm = self.ARM_UP
        self.start_res = (640, 480)

    left_wheel = _make_servo_property(SERVO_LEFT)
    right_wheel = _make_servo_property(SERVO_RIGHT)
    arm = _make_servo_property(SERVO_ARM)

    gate = GPIOProperty(1)
    pump = GPIOProperty(2)

    def battery_level(self):
        return self.motors[0]._tb.GetBatteryReading() * (12.5 / 12.25)

    def move(self, distance):
        multiplier = 1
        if distance < 0:
            multiplier = -1

        self.left_wheel = (self.MULTIPLIER_LEFT * 50 * multiplier)  # - 1
        self.right_wheel = (self.MULTIPLIER_RIGHT * 50 * multiplier)  # - 1

        time.sleep(abs(distance) / self.SPEED_50)

        self.right_wheel = 0
        self.left_wheel = 0

    def turn(self, angle):
        multiplier = 1
        if angle < 0:
            multiplier = -1

        self.left_wheel = self.MULTIPLIER_LEFT * 30 * multiplier
        self.right_wheel = self.MULTIPLIER_RIGHT * -30 * multiplier

        # self.motors[0].led.colour = (255, 0, 0)
        time.sleep(abs(angle) / self.SPEED_ANGULAR_30)

        self.motors[0].led.colour = (255, 255, 255)

        self.right_wheel = 0
        self.left_wheel = 0

    def see(self, *args, **kwargs):
        # Avoid blurring
        time.sleep(0.25)
        # Workaround for bug in sr.robot where the default resolution
        # causes an exception to be raised.
        DEFAULT_RESOLUTION = self.start_res  # (1296, 976)
        if len(args) < 3 and "res" not in kwargs:
            kwargs.update({"res": DEFAULT_RESOLUTION})
        return super(Robot, self).see(*args, **kwargs)

    def pickup_cube(self):
        time.sleep(1)
        self.arm = self.ARM_DOWN
        time.sleep(1)
        self.pump = True
        time.sleep(1)
        self.arm = self.ARM_UP
        time.sleep(0.5)

    def succ(self):
        self.pickup_cube()

    def pump_on(self):
        self.pump = True

    def drop(self):
        self.pump = False

    # def can_see(self, marker_type):
    #     if marker_type is TOKEN:
    #         acceptable_types = [MARKER_TOKEN]
    #         print("Looking for a token...")
    #     elif marker_type is BUCKET:
    #         acceptable_types = [MARKER_BUCKET_SIDE, MARKER_BUCKET_END]
    #         print("Looking for a bucket...")
    #     elif marker_type is WALL:
    #         acceptable_types = [MARKER_ARENA]
    #         print("Looking for a wall...")
    #     else:
    #         raise ValueError("Invalid marker_type")
    #     markers = self.see()
    #     acceptable_markers = [m for m in markers if m.info.marker_type in acceptable_types]
    #     return len(acceptable_markers) > 0

    # Original goto
    # def go_to(self, marker_type):
    #     if marker_type is TOKEN:
    #         acceptable_types = [MARKER_TOKEN]
    #         print("Looking for a token...")
    #     elif marker_type is BUCKET:
    #         acceptable_types = [MARKER_BUCKET_SIDE, MARKER_BUCKET_END]
    #         print("Looking for a bucket...")
    #     else:
    #         raise ValueError("Invalid marker_type")

    #     while True:
    #         markers = self.see()
    #         acceptable_markers = [m for m in markers if m.info.marker_type in acceptable_types]
    #         if acceptable_markers:
    #             dest = acceptable_markers[0]
    #             print("Found marker {} (dist {}, rot_y {})".format(
    #                 dest.info.code, dest.dist, dest.rot_y
    #             ))
    #             self.turn(dest.rot_y)
    #             time.sleep(0.3)
    #             self.move(dest.dist)
    #             return
    #         print("Didn't find any acceptable markers, turning to try again")
    #         self.turn(45)
    #         time.sleep(0.3)

    # Goto with multiple attempts
    # def new_go_to(self, marker_type):

    #     if marker_type is TOKEN:
    #         acceptable_types = [MARKER_TOKEN]
    #         print("Looking for a token...")
    #     elif marker_type is BUCKET:
    #         acceptable_types = [MARKER_BUCKET_SIDE, MARKER_BUCKET_END]
    #         print("Looking for a bucket...")
    #     elif marker_type is WALL:
    #         acceptable_types = [MARKER_ARENA]
    #         print("Looking for a wall...")
    #     else:
    #         raise ValueError("Invalid marker_type")

    #     tries = 0
    #     while tries < 12:
    #         while True:
    #             markers = self.see(res=(1920, 1088))
    #             acceptable_markers = [m for m in markers if m.info.marker_type in acceptable_types]
    #             if acceptable_markers:
    #                 dest = acceptable_markers[0]
    #                 print("Found marker {} (dist {}, rot_y {})".format(
    #                     dest.info.code, dest.dist, dest.rot_y
    #                 ))
    #                 self.turn(dest.rot_y)
    #                 time.sleep(0.3)
    #                 if dest.dist > 0.7:
    #                     self.move(0.5)
    #                     time.sleep(0.3)
    #                 else:
    #                     if not (marker_type is WALL):
    #                         self.move(dest.dist)
    #                     return dest.info.code
    #             else:
    #                 break
    #         print("Didn't find any acceptable markers, turning to try again")
    #         self.turn(60)
    #         time.sleep(0.3)
    #         tries += 1
    #     return -1

    def look_for(self, marker_types, ignored_token_codes=None, sorted_quadrant_index_func=__noop__, resolution=None, clockwise=True):
        if ignored_token_codes is None:
            ignored_token_codes = []
        if resolution is None:
            resolution = self.start_res
        acceptable_types = []
        print("Looking for:")
        if TOKEN in marker_types:
            acceptable_types.append(MARKER_TOKEN)
            print("  - Tokens")
        if BUCKET in marker_types:
            acceptable_types.append(MARKER_BUCKET_SIDE)
            acceptable_types.append(MARKER_BUCKET_END)
            print("  - Buckets")
        if WALL in marker_types:
            # acceptable_types.append(MARKER_ARENA)
            print("  - Walls (after 3rd try)")
        if len(acceptable_types) == 0:
            return [], resolution

        tries = 0
        while tries < 16:
            if (tries == 3) and (WALL in marker_types):
                acceptable_types.append(MARKER_ARENA)
                print("Now looking for walls")
            # One rotation at low res, and if nothing is spotted, one at specified (probably high/zoomed)
            resolution = resolution if tries > 8 else self.start_res
            markers = self.see(res=resolution)
            print(str(resolution))
            # acceptable_markers = [m for m in markers if
            #                       (m.info.marker_type in acceptable_types) and
            #                       not (m.info.code in ignored_token_codes) and
            #                       (not (MARKER_ARENA in acceptable_types) or (
            #                               not (sorted_quadrant_index_func == __noop__) or (
            #                                   sorted_quadrant_index_func(m) == 0 and m.dist > 0.6) or (
            #                                           sorted_quadrant_index_func(m) > 0)
            #                       ))]
            acceptable_markers = []
            for m in markers:
                print("Checking marker {}:".format(m.info.code))

                if m.info.marker_type not in acceptable_types:
                    print("  ❌ Marker is not in acceptable types!")
                    continue

                if m.info.code in ignored_token_codes:
                    print("  ❌ Marker is in ignored codes!")
                    continue

                if MARKER_ARENA in acceptable_types:
                    quadrant = sorted_quadrant_index_func(m)
                    print("  📏 Marker is {}m away".format(m.dist))
                    if quadrant == 0 and m.dist < 1:
                        print("  ❌ Marker is too close to home!")

                print("  ✔️ Marker is good!")
                acceptable_markers.append(m)

            if acceptable_markers:
                print("Found {} markers".format(len(acceptable_markers)))
                return acceptable_markers, resolution
            print("Didn't find any acceptable markers, turning to try again")
            self.turn(45 if clockwise else -45)
            time.sleep(0.3)
            tries += 1
        return [], resolution

    def move_to(self, code, resolution=None):
        if resolution is None:
            resolution = self.start_res
        while True:
            # FIXME: cannot head to marker seen at higher res?
            markers = [m for m in self.see(res=resolution) if m.info.code == code]
            if len(markers) == 0:
                print("Lost marker {}".format(code))
                return False
            marker = markers[0]
            print("Moving to marker {} (dist {}, rot_y {})".format(
                marker.info.code, marker.dist, marker.rot_y
            ))
            self.turn(marker.rot_y)
            time.sleep(0.3)
            if marker.info.marker_type == MARKER_ARENA and marker.dist < 0.4:
                return False
            if marker.dist < 1.5:
                resolution = self.start_res
            if marker.dist > 0.8:
                self.move(0.4)
                time.sleep(0.3)
            else:
                if marker.info.marker_type != MARKER_ARENA:
                    self.move(marker.dist)
                else:
                    return False
                return True

    # Goto with multiple attempts and trig
    # def new_new_go_to(self, marker_type):
    #     if marker_type is TOKEN:
    #         acceptable_types = [MARKER_TOKEN]
    #         print("Looking for a token...")
    #     elif marker_type is BUCKET:
    #         acceptable_types = [MARKER_BUCKET_SIDE, MARKER_BUCKET_END]
    #         print("Looking for a bucket...")
    #     else:
    #         raise ValueError("Invalid marker_type")

    #     while True:
    #         while True:
    #             markers = self.see()
    #             acceptable_markers = [m for m in markers if m.info.marker_type in acceptable_types]
    #             if acceptable_markers:
    #                 dest = acceptable_markers[0]
    #                 print("Found marker {} (dist {}, rot_y {})".format(
    #                     dest.info.code, dest.dist, dest.rot_y
    #                 ))

    #                 if dest.rot_y > 20:
    #                     self.turn(90 - dest.rot_y)
    #                     time.sleep(0.3)
    #                     self.move(dest.dist * math.sin(dest.rot_y))
    #                     time.sleep(0.3)
    #                     self.turn(-90)
    #                 elif dest.rot_y < -20:
    #                     self.turn(-90 + abs(dest.rot_y))
    #                     time.sleep(0.3)
    #                     self.move(dest.dist * math.sin(dest.rot_y))
    #                     time.sleep(0.3)
    #                     self.turn(-90)
    #                 else:
    #                     self.turn(dest.rot_y)
    #                     time.sleep(0.3)
    #                     if dest.dist > 0.6:
    #                         self.move(0.4)
    #                         time.sleep(0.3)
    #                     else:
    #                         self.move(dest.dist)
    #                         return dest.info.code
    #             else:
    #                 break
    #         print("Didn't find any acceptable markers, turning to try again")
    #         self.turn(45)
    #         time.sleep(0.3)
