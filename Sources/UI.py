# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from time import sleep, mktime, strftime
import digitalio
import board
import adafruit_matrixkeypad
import threading
import Sources.RPi_I2C_driver as RPi_I2C_driver 
from datetime import datetime


# VARIABLES PARA EL KEYPAD:
# Filas y columnas con gpios para el keypad
cols = [digitalio.DigitalInOut(x) for x in (board.D26, board.D16, board.D20, board.D21)]
rows = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
# Matriz de valores 4x4 para el Keypad
keys = (('1', '2', '3', 'A'), ('4', '5', '6', 'B'), ('7', '8', '9', 'C'), ('*', '0', '#', 'D'))
# Inicialización del Keypad
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
# Para adquirir el valor del keypad
key_pressed = keypad.pressed_keys
# Booleano para determinar cuándo una tecla fue presionada
action = False

# VARIABLES PARA EL LCD
# Definición de flecha derecha e izquierda para el LCD
fontdata = [
        # Char 0 - left arrow
        [ 0x1,0x3,0x7,0xf,0xf,0x7,0x3,0x1],
        # Char 1 - right arrow
        [ 0x10,0x18,0x1c,0x1e,0x1e,0x1c,0x18,0x10]
]
# Declaración del LCD y limpieza al iniciar el programa
mylcd = RPi_I2C_driver.lcd()
mylcd.lcd_clear()
# Menus Para LCD
screen1_1 = "   BIENVENID@   "
screen2_1 = "POR FAVOR CONFIRMAR FECHA/HORA"
screen3_2 = "A:OK    B:CONFIG"
screen4_2 = "A:CONFIG     B:"
screen5_1 = "CONFIG PROGRAMAS"
screen5_2 = "A:"
screen5_3 =    "   B:OK   C:"

time_string = " "

class Clock:
    def __init__(self):
        self.thread = threading.Thread(target=self._thread)

    def _thread(self):
        print("Clock init")
        global time_string
        time_string = datetime.now().strftime('%d/%m/%y %H:%M')
        dti = mktime(datetime.now().timetuple())-datetime.now().timetuple().tm_sec
        while True:
            ndti = mktime(datetime.now().timetuple())
            if dti+59 < ndti: # cambia cada minuto
                dti = ndti
                time_string=datetime.now().strftime('%d/%m/%y %H:%M')
                sleep(0.95)
            else:
                sleep(0.01)

    def start(self):
        self.thread.start()

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
                    sleep(0.4)
            except Exception as e:
                print("Error",e )
            sleep(1)

    def start(self):
        self.thread.start()


class ActionMenu:
    def __init__(self):
        self.thread = threading.Thread(target=self._thread)

    def _thread(self):
        print("ActionMenu init")
        self.start_screen()
        self.screen2()
        self.screen3()
        while True:
            global action
            if action:
                print(key_pressed)
                action = False

    def start(self):
        self.thread.start()
        
    def start_screen(self):
        for i in range(0,3):
            mylcd.lcd_display_string(screen1_1,1);
            sleep(0.5)
            mylcd.lcd_clear()
            sleep(0.5)
            
    def screen2(self):
        str_pad = " " * 16
        my_long_string = str_pad + screen2_1
        for i in range (0, len(my_long_string)):
            lcd_text = my_long_string[i:(i+16)]
            mylcd.lcd_display_string(lcd_text,1)
            sleep(0.2)
            mylcd.lcd_display_string(str_pad,1)
            
    def screen3(self):
        mylcd.lcd_clear()
        time_string = datetime.now().strftime('%d/%m/%y %H:%M')
        mylcd.lcd_display_string_pos(time_string,1,1)
        mylcd.lcd_display_string(screen3_2,2)
        while True:
            try:
                key_pressed = keypad.pressed_keys
                if key_pressed:
                    if key_pressed[0]=='A':
                        sleep(0.4)
                        self.screen4()
                    elif key_pressed[0]=='B':
                        sleep(0.4)
                        self.screen5()
            except Exception as e:
                print("Error",e )
            sleep(1)
    
    def screen4(self):
        mylcd.lcd_clear()
        time_string = datetime.now().strftime('%d/%m/%y %H:%M')
        mylcd.lcd_display_string_pos(time_string,1,1)
        mylcd.lcd_display_string(screen4_2,2)
        mylcd.lcd_load_custom_chars(fontdata)
        mylcd.lcd_display_string_pos(chr(1),2,15)
        while action == False:
            try:
                key_pressed = keypad.pressed_keys
                if key_pressed:
                    if key_pressed[0]=='A':
                        sleep(0.4)
                        self.screen3()
                    elif key_pressed[0]=='B':
                        sleep(0.4)
                        self.screen5()
            except Exception as e:
                print("Error",e )
                
    def screen5(self):
        mylcd.lcd_clear()
        mylcd.lcd_display_string(screen5_1,1)
        mylcd.lcd_display_string(screen5_2,2)
        mylcd.lcd_load_custom_chars(fontdata)
        mylcd.lcd_display_string_pos(chr(0),2,2)
        mylcd.lcd_display_string_pos(screen5_3,2,3)
        mylcd.lcd_display_string_pos(chr(1),2,15)
#         while action == False:
#             try:
#                 key_pressed = keypad.pressed_keys
#                 if key_pressed[0]=='A':
#                     action = True
#                     self.screen3()
#                     #print(key_pressed)
#                     sleep(0.4)
#                 elif key_pressed[0]=='B':
#                     action = True
#                     self.screen5()
#             except Exception as e:
#                 print("Error",e )

        
        


