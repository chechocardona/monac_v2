# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import digitalio
import board
import adafruit_matrixkeypad
import threading

# Membrane 4x4 matrix keypad on Raspberry Pi -
cols = [digitalio.DigitalInOut(x) for x in (board.D26, board.D16, board.D20, board.D21)]
rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]

# 4x4 matrix keypad on Raspberry Pi -
keys = (('1', '2', '3', 'A'), ('4', '5', '6', 'B'), ('7', '8', '9', 'C'), ('*', '0', '#', 'D'))

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
key_pressed = keypad.pressed_keys
action = False

class Keys:
    def __init__(self):
        self.thread = threading.Thread(target=self._thread)

    def _thread(self):
        print("Keys init")
        while True:
            try:
                global key_pressed
                key_pressed = keypad.pressed_keys
                if key_pressed:
                    global action
                    action = True
                    #print(key_pressed)
                    time.sleep(0.4)
            except Exception as e:
                print("Error",e )

    def start(self):
        self.thread.start()


class ActionMenu:
    def __init__(self):
        self.thread = threading.Thread(target=self._thread)

    def _thread(self):
        print("ActionMenu init")
        while True:
            global action
            if action:
                print(key_pressed)
                action = False

    def start(self):
        self.thread.start()

#while True:
#    try:
#        keys = keypad.pressed_keys
#        if keys:
#            print(keys)
#            time.sleep(0.4)
#    except Exception as e:
#        print("Error",e)
