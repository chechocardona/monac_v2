# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from time import sleep, mktime, strftime
import digitalio
import board
import adafruit_matrixkeypad
import threading
import Sources.RPi_I2C_driver as RPi_I2C_driver 
from datetime import datetime
import subprocess


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
screen1a = "   BIENVENID@"
screen2a = "PRESIONE 'C' PARA CONFIRMAR FECHA(DD/MM/AA) y HORA o PRESIONE 'A' PARA CONFIGURAR"
screen3b = "A:CONF C:OK"
screen4b = "A:"
screen4c =    "          B:"
screen5a = "CONFIG PROGRAMAS"
screen5b = "A:"
screen5c =    "   C:OK   B:"
screen6a = "     GRABAR"
screen6b = "A:"
screen6c =    "   C:OK"
screen8a = "ERR:conf invalid"
screen8b = "      C:OK"

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
        self.menu = 3
        self.action = False

    def _thread(self):
        print("ActionMenu init")
        #self.start_screen()
        #self.info_screen()
        while True:
            self.menu_navig()

    def start(self):
        self.thread.start()
        
    def start_screen(self):
        for i in range(0,3):
            mylcd.lcd_display_string(screen1a,1);
            sleep(0.5)
            mylcd.lcd_clear()
            sleep(0.5)
            
    def info_screen(self):
        str_pad = " " * 16
        my_long_string = str_pad + screen2a
        for i in range (0, len(my_long_string)):
            lcd_text = my_long_string[i:(i+16)]
            mylcd.lcd_display_string(lcd_text,1)
            sleep(0.15)
            mylcd.lcd_display_string(str_pad,1)
            
    def menu_navig(self):
        if self.menu==3:
            mylcd.lcd_clear()
            self.action = False
            # LCD config
            time_string = datetime.now().strftime('%d/%m/%y %H:%M')
            mylcd.lcd_display_string_pos(time_string,1,1)
            mylcd.lcd_display_string(screen3b,2)
            while self.action==False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        if key_pressed[0]=='C':
                            sleep(0.4)
                            self.menu = 4
                            self.action = True
                        elif key_pressed[0]=='A':
                            sleep(0.4)
                            self.menu = 7
                            self.action = True
                except Exception as e:
                    print("Error",e )
                    
        elif self.menu==4:
            mylcd.lcd_clear()
            self.action = False
            # LCD config
            time_string = datetime.now().strftime('%d/%m/%y %H:%M')
            mylcd.lcd_display_string_pos(time_string,1,1)
            mylcd.lcd_display_string(screen4b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen4c,2,3)
            mylcd.lcd_display_string_pos(chr(1),2,15)
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        if key_pressed[0]=='A':
                            sleep(0.4)
                            self.menu=3
                            self.action = True
                        elif key_pressed[0]=='B':
                            sleep(0.4)
                            self.menu=5
                            self.action = True
                except Exception as e:
                    print("Error",e )
                    
        elif self.menu==5:
            mylcd.lcd_clear()
            self.action = False
            # LCD config
            mylcd.lcd_display_string(screen5a,1)
            mylcd.lcd_display_string(screen5b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen5c,2,3)
            mylcd.lcd_display_string_pos(chr(1),2,15)
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        if key_pressed[0]=='A':
                            sleep(0.4)
                            self.menu=4
                            self.action = True
                        elif key_pressed[0]=='C':
                            sleep(0.4)
                            self.menu=5
                            self.action = True
                        elif key_pressed[0]=='B':
                            sleep(0.4)
                            self.menu=6
                            self.action = True
                except Exception as e:
                    print("Error",e )
                    
        elif self.menu==6:
            mylcd.lcd_clear()
            self.action = False
            # LCD config
            mylcd.lcd_display_string(screen6a,1)
            mylcd.lcd_display_string(screen6b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen6c,2,3)
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        if key_pressed[0]=='A':
                            sleep(0.4)
                            self.menu=5
                            self.action = True
                        elif key_pressed[0]=='C':
                            sleep(0.4)
                            self.menu=6
                            self.action = True
                except Exception as e:
                    print("Error",e )
        
        # Menú de configuración de Hora/Fecha
        if self.menu==7:
            mylcd.lcd_clear()
            self.action = False
            # LCD config
            time_string = datetime.now().strftime('%d/%m/%y %H:%M')
            mylcd.lcd_display_string_pos(time_string,1,1)
            mylcd.lcd_display_string(screen5b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen5c,2,3)
            mylcd.lcd_display_string_pos(chr(1),2,15)
            cursor = 1
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        if key_pressed[0]=='A':
                            sleep(0.4)
                            if cursor > 1:
                                cursor=cursor-1
                                if cursor%3==0:
                                    cursor=cursor-1
                                mylcd.lcd_display_string_pos(time_string,1,1)
                        elif key_pressed[0]=='C':
                            sleep(0.4)
                            date="--date=20"+time_string[6:8]+"-"+time_string[3:5]+"-"+time_string[0:2]+" "+\
                                  time_string[9:11]+":"+time_string[12:14]+":00"
                            resp=subprocess.run(["sudo","hwclock","--set",date], capture_output=True)
                            if resp.stderr.find(b"invalid")>-1:
                                self.menu=8
                            else:
                                subprocess.run(["sudo","hwclock","-s"])
                                self.menu=4
                            self.action = True
                        elif key_pressed[0]=='B':
                            if cursor!=2 and cursor!=5 and cursor!=11 and cursor!=8 or \
                               (cursor==2 and time_string[0]!='3') or (cursor==5 and time_string[3]!='1') or \
                               (cursor==11 and time_string[9]!='2') or (cursor==8 and time_string[6]!='2'):
                                sleep(0.4)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1
                                    mylcd.lcd_display_string_pos(time_string,1,1)
                        # Condiciones para la detección de los números
                        elif key_pressed[0]=='0':
                            if cursor!=7 and cursor!=8 or (cursor==8 and time_string[6]!='2'):
                                time_string=time_string[:cursor-1] + '0' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1
                        elif key_pressed[0]=='1':
                            if cursor!=7 and cursor!=8 or (cursor==8 and time_string[6]!='2'):
                                time_string=time_string[:cursor-1] + '1' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1
                        elif key_pressed[0]=='2':
                            if cursor!=4 and cursor!=2 or (cursor==2 and time_string[0]!='3'):
                                time_string=time_string[:cursor-1] + '2' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1
                        elif key_pressed[0]=='3':
                            if cursor!=4 and cursor!=10 and cursor!=2 and cursor!=5 or \
                               (cursor==2 and time_string[0]!='3') or (cursor==5 and time_string[3]!='1'):
                                time_string=time_string[:cursor-1] + '3' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1                         
                        elif key_pressed[0]=='4':
                            if cursor!=4 and cursor!=10 and cursor!=1 and cursor!=2 and cursor!=5 and cursor!=11 or \
                               (cursor==2 and time_string[0]!='3') or (cursor==5 and time_string[3]!='1') or \
                               (cursor==11 and time_string[9]!='2'):
                                time_string=time_string[:cursor-1] + '4' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1
                        elif key_pressed[0]=='5':
                            if cursor!=4 and cursor!=10 and cursor!=1 and cursor!=2 and cursor!=5 and cursor!=11 or \
                               (cursor==2 and time_string[0]!='3') or (cursor==5 and time_string[3]!='1') or \
                               (cursor==11 and time_string[9]!='2'):
                                time_string=time_string[:cursor-1] + '5' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1                            
                        elif key_pressed[0]=='6':
                            if cursor!=4 and cursor!=10 and cursor!=1 and cursor != 13 and cursor!=2 and \
                               cursor!=5 and cursor!=11 or (cursor==2 and time_string[0]!='3') or \
                               (cursor==5 and time_string[3]!='1') or (cursor==11 and time_string[9]!='2'):
                                time_string=time_string[:cursor-1] + '6' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1                           
                        elif key_pressed[0]=='7':
                            if cursor!=4 and cursor!=10 and cursor!=1 and cursor != 13 and cursor!=2 and \
                               cursor!=5 and cursor!=11 or (cursor==2 and time_string[0]!='3') or \
                               (cursor==5 and time_string[3]!='1') or (cursor==11 and time_string[9]!='2'):
                                time_string=time_string[:cursor-1] + '7' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1                            
                        elif key_pressed[0]=='8':
                            if cursor!=4 and cursor!=10 and cursor!=1 and cursor != 13 and cursor!=2 and \
                               cursor!=5 and cursor!=11 or (cursor==2 and time_string[0]!='3') or \
                               (cursor==5 and time_string[3]!='1') or (cursor==11 and time_string[9]!='2'):
                                time_string=time_string[:cursor-1] + '8' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1
                        elif key_pressed[0]=='9':
                            if cursor!=4 and cursor!=10 and cursor!=1 and cursor != 13 and cursor!=2 and \
                               cursor!=5 and cursor!=11 or (cursor==2 and time_string[0]!='3') or \
                               (cursor==5 and time_string[3]!='1') or (cursor==11 and time_string[9]!='2'):
                                time_string=time_string[:cursor-1] + '9' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,1)
                                if cursor < 14:
                                    cursor=cursor+1
                                    if cursor%3==0:
                                        cursor=cursor+1
                except Exception as e:
                    print("Error",e )
                    
                mylcd.lcd_display_string_pos(time_string[cursor-1],1,cursor);
                sleep(0.2)
                mylcd.lcd_display_string_pos(' ',1,cursor);
                sleep(0.2)
                
        # Menu de error para la configuración de fecha
        elif self.menu==8:
            mylcd.lcd_clear()
            self.action = False
            mylcd.lcd_display_string(screen8a,1)
            mylcd.lcd_display_string(screen8b,2)
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        if key_pressed[0]=='C':
                            sleep(0.4)
                            self.menu=7
                            self.action = True
                except Exception as e:
                    print("Error",e )
    
                  
    
        


