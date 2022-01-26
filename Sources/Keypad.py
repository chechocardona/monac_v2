# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import digitalio
import board
import adafruit_matrixkeypad

# Membrane 4x4 matrix keypad on Raspberry Pi -
cols = [digitalio.DigitalInOut(x) for x in (board.D26, board.D16, board.D20, board.D21)]
rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]

# 4x4 matrix keypad on Raspberry Pi -
keys = (('1', '2', '3', 'A'), ('4', '5', '6', 'B'), ('7', '8', '9', 'C'), ('*', '0', '#', 'D'))

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

while True:
    keys = keypad.pressed_keys
    if keys:
        print("Pressed: ", keys)
        time.sleep(0.4)