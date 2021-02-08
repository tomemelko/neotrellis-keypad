#  Launch Deck Trellis M4
#  USB HID button box for launching applications, media control, camera switching and more
#  Use it with your favorite keyboard controlled launcher, such as Quicksilver and AutoHotkey

import time
import random
import adafruit_trellism4
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.gamepad import Gamepad
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Rotation of the trellis. 0 is when the USB is upself.
# The grid coordinates used below require portrait mode of 90 or 270
ROTATION = 90

# the two command types -- MEDIA for ConsumerControlCodes, KEY for Keycodes
# this allows button press to send the correct HID command for the type specified
MEDIA = 1
KEY = 2
MODE = 3
GAMEPAD = 4
brightnessFactor = 0.1
# button mappings
# customize these for your desired postitions, colors, and keyboard combos
# specify (button coordinate): (color hex value, command type, command/keycodes)
keymaps = [
    {
        (0,0): (0x00FF00, KEY, (Keycode.F5,)),
        (1,0): (0xFFFF00, KEY, (Keycode.F9,)),
        (2,0): (0xFF00FF, KEY, (Keycode.F11,)),
        (3,0): (0x00FFFF, KEY, (Keycode.F10,)),

        (0,1): (0xFF0000, KEY, (Keycode.SHIFT, Keycode.F5)),
        (2,1): (0x0000FF, KEY, (Keycode.SHIFT, Keycode.F11)),
        (3,1): (0xFFFFFF, MODE, ()),

        (0,2): (0xFF0055, KEY, (Keycode.F2,)),
        (1,2): (0x5500FF, KEY, (Keycode.F12,)),

        (0,3): (0xFFFF00, KEY, (Keycode.COMMAND, Keycode.K)),
        (1,3): (0x00FF00, KEY, (Keycode.COMMAND, Keycode.OPTION, Keycode.S)),
        (2,3): (0xFF0000, KEY, (Keycode.COMMAND, Keycode.R)),
        (0,5): (0x22FF22, KEY, (Keycode.KEYPAD_EIGHT,)),
        (1,5): (0xFF2222, KEY, (Keycode.KEYPAD_NINE,)),
        # (2,5): (0xFFFF00, KEY, (Keycode.KEYPAD_SIX,)),
        # (3,5): (0xFF6666, KEY, (Keycode.KEYPAD_SEVEN,)),
        (0,6): (0x00FF00, KEY, (Keycode.KEYPAD_FOUR,)),
        (1,6): (0xFF0000, KEY, (Keycode.KEYPAD_FIVE,)),
        (2,6): (0xFFFF00, KEY, (Keycode.KEYPAD_SIX,)),
        (3,6): (0xFF6666, KEY, (Keycode.KEYPAD_SEVEN,)),
        (0,7): (0x666666, KEY, (Keycode.KEYPAD_ZERO,)),
        (1,7): (0x0000FF, KEY, (Keycode.KEYPAD_ONE,)),
        (2,7): (0x00FF00, KEY, (Keycode.KEYPAD_TWO,)),
        (3,7): (0xFF0000, KEY, (Keycode.KEYPAD_THREE,)),
    },
    {
        (3,1): (0xFFFFFF, MODE, ()),

        (3,3): (0xFFFFFF, KEY, (Keycode.BACKSPACE,)),
        (3,4): (0xFF00AA, KEY, (Keycode.F,)),
        (2,4): (0xFF00FF, KEY, (Keycode.E,)),
        (1,4): (0xAA00FF, KEY, (Keycode.D,)),
        (0,4): (0x5500FF, KEY, (Keycode.C,)),
        (3,5): (0x0000FF, KEY, (Keycode.B,)),
        (2,5): (0x0055FF, KEY, (Keycode.A,)),
        (1,5): (0x00AAFF, KEY, (Keycode.NINE,)),
        (0,5): (0x00FFFF, KEY, (Keycode.EIGHT,)),
        (3,6): (0x00FFAA, KEY, (Keycode.SEVEN,)),
        (2,6): (0x00FF55, KEY, (Keycode.SIX,)),
        (1,6): (0x55FF00, KEY, (Keycode.FIVE,)),
        (0,6): (0xAAFF00, KEY, (Keycode.FOUR,)),
        (3,7): (0xFFFF00, KEY, (Keycode.THREE,)),
        (2,7): (0xFFAA00, KEY, (Keycode.TWO,)),
        (1,7): (0xFF5500, KEY, (Keycode.ONE,)),
        (0,7): (0xFF0000, KEY, (Keycode.ZERO,)),
    }
]

# Time in seconds to stay lit before sleeping.
TIMEOUT = 60 * 10

# Time to take fading out all of the keys.
FADE_TIME = 1

# Once asleep, how much time to wait between "snores" which fade up and down one button.
SNORE_PAUSE = 0.5

# Time in seconds to take fading up the snoring LED.
SNORE_UP = 2

# Time in seconds to take fading down the snoring LED.
SNORE_DOWN = 1

TOTAL_SNORE = SNORE_PAUSE + SNORE_UP + SNORE_DOWN

mode = 0

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
gp = Gamepad(usb_hid.devices)

trellis = adafruit_trellism4.TrellisM4Express(rotation=ROTATION)
trellis.pixels.brightness = brightnessFactor

current_press = set()
last_press = time.monotonic()
nore_count = -1

def set_state():
    keymap = keymaps[mode]
    for button in keymap:
        trellis.pixels[button] = keymap[button][0]

set_state()

while True:
    keymap = keymaps[mode]
    pressed = set(trellis.pressed_keys)
    now = time.monotonic()
    sleep_time = now - last_press
    sleeping = sleep_time > TIMEOUT
    for down in pressed - current_press:
        if down in keymap and not sleeping:
            print("down", down)
            # Lower the brightness so that we don't draw too much current when we turn all of
            # the LEDs on.
            trellis.pixels.brightness = 0.2 * brightnessFactor
            trellis.pixels.fill(keymap[down][0])
            if keymap[down][1] == KEY:
                print(keymap[down][2])
                if len(keymap[down][2]) == 1:
                    kbd.send(keymap[down][2][0])
                else:
                    kbd.press(*keymap[down][2])
            elif keymap[down][1] == MODE:
                mode = (mode + 1) % len(keymaps)
                set_state()
            elif keymap[down][1] == GAMEPAD:
                gp.click_buttons(keymap[down][2])
            else:
                cc.send(keymap[down][2])
            # else if the entry starts with 'l' for layout.write
        last_press = now
    for up in current_press - pressed:
        if up in keymap:
            print("up", up)
            if keymap[up][1] == KEY and len(keymap[down][2]) > 1:
                kbd.release(*keymap[up][2])

    # Reset the LEDs when there was something previously pressed (current_press) but nothing now
    # (pressed).
    if not pressed and current_press:
        trellis.pixels.brightness = 1 * brightnessFactor
        trellis.pixels.fill((0, 0, 0))
        for button in keymap:
            trellis.pixels[button] = keymap[button][0]

    if not sleeping:
        snore_count = -1
    else:
        sleep_time -= TIMEOUT
        # Fade all out
        if sleep_time < FADE_TIME:
            brightness = (1 - sleep_time / FADE_TIME)
        # Snore by pausing and then fading a random button up and back down.
        else:
            sleep_time -= FADE_TIME
            current_snore = int(sleep_time / TOTAL_SNORE)
            # Detect a new snore and pick a new button
            if current_snore > snore_count:
                button = random.choice(list(keymap.keys()))
                trellis.pixels.fill((0, 0, 0))
                trellis.pixels[button] = keymap[button][0]
                snore_count = current_snore

            sleep_time = sleep_time % TOTAL_SNORE
            if sleep_time < SNORE_PAUSE:
                brightness = 0
            else:
                sleep_time -= SNORE_PAUSE
                if sleep_time < SNORE_UP:
                    brightness = sleep_time / SNORE_UP
                else:
                    sleep_time -= SNORE_UP
                    brightness = 1 - sleep_time / SNORE_DOWN
        trellis.pixels.brightness = brightness * brightnessFactor
    current_press = pressed