from time import sleep, mktime, strftime, perf_counter
import digitalio
import board
import adafruit_matrixkeypad
import threading
import Sources.RPi_I2C_driver as RPi_I2C_driver 
from datetime import datetime
import subprocess
import configparser


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
        [ 0x10,0x18,0x1c,0x1e,0x1e,0x1c,0x18,0x10],
        # Char 2 - up arrow
        [ 0x04,0x0E,0x1F,0x04,0x04,0x04,0x04,0x00]
]
# Declaración del LCD y limpieza al iniciar el programa
mylcd = RPi_I2C_driver.lcd()
mylcd.lcd_clear()
# Menus Para LCD
screen1a    = "   BIENVENID@"
screen2a    = "PRESIONE 'B' PARA CONFIRMAR FECHA(DD/MM/AA) y HORA(24H) o PRESIONE 'A' PARA CONFIGURAR"
screen3b    = "A:CONFIG    B:OK"
screen4b    = "A:"
screen4c    =    "          B:"
screen5a    = "CONFIG PROGRAMAS"
screen5b    = "A:"
screen5c    =    "   C:OK   B:"
screen6a    = "     GRABAR"
screen6b    = "A:"
screen6c    =    "   C:OK"
screen8a    = "ERR:conf invalid"
screen8b    = "      C:OK"
screen9a    = "   PROGRAMA "
screen10a   = " inicio: "
screen10b   = "A:"
screen10c   =    " C:OK D:"
screen10d   =             " B:"
screen10a_2 = "    fin: "
message2    = "PROGRAMA GUARDADO!"
error       = "POR FAVOR CONFIGURE UNA HORA VALIDA"
error2      = "LA HORA DE INICIO NO PUEDE SER MENOR O IGUAL A LA HORA FINAL"
error3      = "AL MENOS UN DIA DEBE SER SELECCIONADO PARA ACTIVAR EL PROG."

# VARIABLES PARA REVISAR EL INICIO DE LA GRABACIÓN AUTOMáTICA


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
        self.current_menu=0
        self.sleep_secs = 45
        self.program = 1
        self.inicio = True
        self.config = configparser.ConfigParser()

    def _thread(self):
        print("ActionMenu init")
        #self.start_screen()
        #self.info_screen(screen2a)
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
                        
    def info_screen(self, text):
        str_pad = " " * 16
        my_long_string = str_pad + text
        for i in range (0, len(my_long_string)):
            lcd_text = my_long_string[i:(i+16)]
            mylcd.lcd_display_string(lcd_text,1)
            sleep(0.15)
            mylcd.lcd_display_string(str_pad,1)
            
    def menu_navig(self):
        if self.menu==0:
            mylcd.lcd_clear()
            self.action = False
            mylcd.backlight(0)
            while self.action==False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        sleep(0.4)
                        self.menu = self.current_menu
                        self.action = True
                except Exception as e:
                    print("Error",e )
                sleep(1)
    
        elif self.menu==3:
            mylcd.lcd_clear()
            self.action = False
            # LCD config
            time_string = datetime.now().strftime('%d/%m/%y %H:%M')
            mylcd.lcd_display_string_pos(time_string,1,1)
            mylcd.lcd_display_string(screen3b,2)
            # Timer to put a black screen
            start=int(perf_counter())
            while self.action==False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        if key_pressed[0]=='B':
                            sleep(0.4)
                            self.menu = 4
                            self.action = True
                        elif key_pressed[0]=='A':
                            sleep(0.4)
                            self.menu = 7
                            self.action = True
                except Exception as e:
                    print("Error",e )
                    
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                    
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
            # Timer to put a black screen
            start=int(perf_counter())
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
                
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                    
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
            # Timer to put a black screen
            start=int(perf_counter())
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
                            self.menu=9
                            self.action = True
                        elif key_pressed[0]=='B':
                            sleep(0.4)
                            self.menu=6
                            self.action = True
                except Exception as e:
                    print("Error",e )
                
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                    
        elif self.menu==6:
            mylcd.lcd_clear()
            self.action = False
            # LCD config
            mylcd.lcd_display_string(screen6a,1)
            mylcd.lcd_display_string(screen6b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen6c,2,3)
            # Timer to put a black screen
            start=int(perf_counter())
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
                    
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
        
        # Menú de configuración de Hora/Fecha
        elif self.menu==7:
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
            # Timer to put a black screen
            start=int(perf_counter())
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        start=int(perf_counter())
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
                            if cursor!=2 and cursor!=5 and cursor!=11  or \
                               (cursor==2 and time_string[0]!='3') or \
                               (cursor==2 and time_string[0]=='3' and time_string[1]<'2') or \
                               (cursor==5 and time_string[3]!='1') or \
                               (cursor==5 and time_string[3]=='1' and time_string[4]<'3') or \
                               (cursor==11 and time_string[9]!='2') or \
                               (cursor==11 and time_string[9]=='2' and time_string[10]<'4'):
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
                  
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                
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
            start=int(perf_counter())
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
                    
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                    
        # Menu de configuración de programas
        elif self.menu==9:
            mylcd.lcd_clear()
            self.action = False
            texto = screen9a + str(self.program)
            mylcd.lcd_display_string(texto,1)
            mylcd.lcd_display_string(screen5b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen5c,2,3)
            mylcd.lcd_display_string_pos(chr(1),2,15)
            # Timer to put a black screen
            start=int(perf_counter())
            
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        start=int(perf_counter())
                        if key_pressed[0]=='A':
                            sleep(0.4)
                            if self.program == 1:
                                self.menu=5
                                self.action=True
                            elif self.program > 1 and self.program < 5:
                                self.program = self.program-1
                                texto = screen9a + str(self.program)
                                mylcd.lcd_display_string(texto,1)
                            elif self.program == 5:
                                mylcd.lcd_clear()
                                self.program = self.program-1
                                texto = screen9a + str(self.program)
                                mylcd.lcd_display_string(texto,1)
                                mylcd.lcd_display_string(screen5b,2)
                                mylcd.lcd_load_custom_chars(fontdata)
                                mylcd.lcd_display_string_pos(chr(0),2,2)
                                mylcd.lcd_display_string_pos(screen5c,2,3)
                                mylcd.lcd_display_string_pos(chr(1),2,15)
                        elif key_pressed[0]=='C':
                            sleep(0.4)
                            self.action = True
                            self.menu = 10
                            self.inicio=True
                        elif key_pressed[0]=='B':
                            sleep(0.4)
                            if self.program < 4:
                                self.program = self.program+1
                                texto = screen9a + str(self.program)
                                mylcd.lcd_display_string(texto,1)
                            elif self.program == 4:
                                mylcd.lcd_clear()
                                self.program = self.program+1
                                texto = screen9a + str(self.program)
                                mylcd.lcd_display_string(texto,1)
                                mylcd.lcd_display_string(screen6b,2)
                                mylcd.lcd_load_custom_chars(fontdata)
                                mylcd.lcd_display_string_pos(chr(0),2,2)
                                mylcd.lcd_display_string_pos(screen6c,2,3)
                            
                except Exception as e:
                    print("Error",e )
                    
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                    
        # Menu de configuración de tiempo de programas
        elif self.menu==10:
            mylcd.lcd_clear()
            self.action = False
            # Adquirir el valor de la hora de archivo de configuración
            self.config.read("programs.ini")
            prog = "program"+str(self.program)
            if self.inicio:
                time_string = self.config.get(prog,"start")
                texto = screen10a + time_string
            else:
                time_string = self.config.get(prog,"end")
                texto = screen10a_2 + time_string
                
            mylcd.lcd_display_string(texto,1)
            mylcd.lcd_display_string(screen10b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen10c,2,3)
            mylcd.lcd_display_string_pos(chr(2),2,11)
            mylcd.lcd_display_string_pos(screen10d,2,12)
            mylcd.lcd_display_string_pos(chr(1),2,15)
            # Timer to put a black screen
            start=int(perf_counter())
            cursor=1
            
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        start=int(perf_counter())
                        if key_pressed[0]=='A':
                            sleep(0.4)
                            if cursor > 1:
                                cursor=cursor-1
                                if cursor==3:
                                    cursor=cursor-1
                                mylcd.lcd_display_string_pos(time_string,1,9)
                        elif key_pressed[0]=='C':
                            sleep(0.4)
                            ## Logica para grabar la hora de inicio y de fin
                            if self.inicio:
                                if int(time_string[0:2])<24 and int(time_string[3:]) < 60:
                                    self.config[prog]['start']=time_string
                                    with open('programs.ini', 'w') as configfile:
                                        self.config.write(configfile)
                                    self.menu=10
                                    self.action = True
                                    self.inicio = False
                                else:
                                    self.info_screen(error)
                                    self.menu=10
                                    self.action = True
                                    self.inicio = True
                            else:
                                time1 = self.config[prog]['start']
                                if (int(time_string[0:2])<24 and int(time_string[3:]) < 60):
                                    
                                    if (time1[0:2]<time_string[0:2]) or (time1[0:2]==time_string[0:2] and \
                                                                         time1[3:]<time_string[3:]):
                                        self.config[prog]['end']=time_string
                                        with open('programs.ini', 'w') as configfile:
                                            self.config.write(configfile)
                                        self.menu=11
                                        self.action=True
                                    else:
                                        self.info_screen(error2)
                                        self.menu=10
                                        self.action=True
                                else:
                                    self.info_screen(error)
                                    self.menu=10
                                    self.action=True
                        elif key_pressed[0]=='B':
                            sleep(0.4)
                            if cursor!=2 or (cursor==2 and time_string[0]!='2') or \
                               (cursor==2 and time_string[0]=='2' and time_string[1]<'4'):
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1
                                    mylcd.lcd_display_string_pos(time_string,1,9)
                        # Regresa al menu anterior
                        elif key_pressed[0]=='D':
                            sleep(0.4)
                            if self.inicio:
                                self.menu=9
                                self.action=True
                            else:
                                self.menu=10
                                self.inicio=True
                                self.action=True
                        # Condiciones para la detección de los números
                        elif key_pressed[0]=='0':
                            time_string=time_string[:cursor-1] + '0' + time_string[cursor:]
                            mylcd.lcd_display_string_pos(time_string,1,9)
                            if cursor < 5:
                                cursor=cursor+1
                                if cursor==3:
                                    cursor=cursor+1
                        elif key_pressed[0]=='1':
                            time_string=time_string[:cursor-1] + '1' + time_string[cursor:]
                            mylcd.lcd_display_string_pos(time_string,1,9)
                            if cursor < 5:
                                cursor=cursor+1
                                if cursor==3:
                                    cursor=cursor+1
                        elif key_pressed[0]=='2':
                            time_string=time_string[:cursor-1] + '2' + time_string[cursor:]
                            mylcd.lcd_display_string_pos(time_string,1,9)
                            if cursor < 5:
                                cursor=cursor+1
                                if cursor==3:
                                    cursor=cursor+1
                        elif key_pressed[0]=='3':
                            if cursor!=1:
                                time_string=time_string[:cursor-1] + '3' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,9)
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1                         
                        elif key_pressed[0]=='4':
                            if cursor!=1 and cursor!=2 or (cursor==2 and time_string[0]!='2'):
                                time_string=time_string[:cursor-1] + '4' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,9)
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1
                        elif key_pressed[0]=='5':
                            if cursor!=1 and cursor!=2 or (cursor==2 and time_string[0]!='2'):
                                time_string=time_string[:cursor-1] + '5' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,9)
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1                            
                        elif key_pressed[0]=='6':
                            if cursor!=1 and cursor!=2 and cursor!=4 or (cursor==2 and time_string[0]!='2'):
                                time_string=time_string[:cursor-1] + '6' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,9)
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1                           
                        elif key_pressed[0]=='7':
                            if cursor!=1 and cursor!=2 and cursor!=4 or (cursor==2 and time_string[0]!='2'):
                                time_string=time_string[:cursor-1] + '7' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,9)
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1                            
                        elif key_pressed[0]=='8':
                            if cursor!=1 and cursor!=2 and cursor!=4 or (cursor==2 and time_string[0]!='2'):
                                time_string=time_string[:cursor-1] + '8' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,9)
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1
                        elif key_pressed[0]=='9':
                            if cursor!=1 and cursor!=2 and cursor!=4 or (cursor==2 and time_string[0]!='2'):
                                time_string=time_string[:cursor-1] + '9' + time_string[cursor:]
                                mylcd.lcd_display_string_pos(time_string,1,9)
                                if cursor < 5:
                                    cursor=cursor+1
                                    if cursor==3:
                                        cursor=cursor+1
                                
                except Exception as e:
                    print("Error",e )
                    
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                    
                mylcd.lcd_display_string_pos(time_string[cursor-1],1,cursor+8);
                sleep(0.2)
                mylcd.lcd_display_string_pos(' ',1,cursor+8);
                sleep(0.2)
    
        # Menu de ajuste de días
        elif self.menu==11:
            mylcd.lcd_clear()
            self.action=False
            cursor=1
            self.config.read("programs.ini")
            prog = "program"+str(self.program)
            day1 = self.config.get(prog,"monday")
            day2 = self.config.get(prog,"tuesday")
            day3 = self.config.get(prog,"wednesday")
            day4 = self.config.get(prog,"thursday")
            day5 = self.config.get(prog,"friday")
            day6 = self.config.get(prog,"saturday")
            day7 = self.config.get(prog,"sunday")
            days=[day1,day2,day3,day4,day5,day6,day7]
            text = " L M M J V S D "
            for idx, x in enumerate(days):
                if(x)=='True':
                    text=text[:(idx*2+2)]+'*'+text[(idx*2+2)+1:]
                          
            mylcd.lcd_display_string(text,1)           
            mylcd.lcd_display_string(screen10b,2)
            mylcd.lcd_load_custom_chars(fontdata)
            mylcd.lcd_display_string_pos(chr(0),2,2)
            mylcd.lcd_display_string_pos(screen10c,2,3)
            mylcd.lcd_display_string_pos(chr(2),2,11)
            mylcd.lcd_display_string_pos(screen10d,2,12)
            mylcd.lcd_display_string_pos(chr(1),2,15)
            # Timer to put a black screen
            start=int(perf_counter())
            cursor=1
            
            while self.action == False:
                try:
                    key_pressed = keypad.pressed_keys
                    if key_pressed:
                        start=int(perf_counter())
                        if key_pressed[0]=='A':
                            sleep(0.4)
                            if cursor > 1:
                                cursor=cursor-2
                            mylcd.lcd_display_string(text,1)
                        elif key_pressed[0]=='C':
                            sleep(0.4)
                            if cursor < 13:
                                if text[cursor+1]==' ':
                                    text=text[:cursor+1] + '*' + text[cursor+2:]
                                    days[int((cursor-1)/2)]='True'
                                else:
                                    text=text[:cursor+1] + ' ' + text[cursor+2:]
                                    days[int((cursor-1)/2)]='False'
                                cursor=cursor+2
                            else:
                                if text[14]==' ':
                                    text=text[:cursor+1] + '*'
                                    days[6]='True'
                                else:
                                    text=text[:cursor+1] + ' '
                                    days[6]='False'
                            mylcd.lcd_display_string(text,1)
                            
                        elif key_pressed[0]=='B':
                            sleep(0.4)
                            if cursor < 13:
                                cursor=cursor+2
                                mylcd.lcd_display_string(text,1)
                            else:
                                self.config[prog]['monday']=days[0]
                                self.config[prog]['tuesday']=days[1]
                                self.config[prog]['wednesday']=days[2]
                                self.config[prog]['thursday']=days[3]
                                self.config[prog]['friday']=days[4]
                                self.config[prog]['saturday']=days[5]
                                self.config[prog]['sunday']=days[6]
                                false_count=0
                                for x in days:
                                    if x == 'True':
                                        self.config[prog]['init']='True'
                                        with open('programs.ini', 'w') as configfile:
                                            self.config.write(configfile)
                                        break
                                    else:
                                        false_count=false_count+1
                                            
                                if false_count==7:
                                    self.info_screen(error3)
                                    self.menu=11
                                    self.action=True
                                else:
                                    mylcd.lcd_clear()
                                    self.info_screen(message2)
                                    self.menu=9
                                    self.action=True
                        # Regresa al menu anterior
                        elif key_pressed[0]=='D':
                            sleep(0.4)
                            self.menu=10
                            self.action=True
                        
                except Exception as e:
                    print("Error",e )
                    
                if int(perf_counter())-start > self.sleep_secs:
                    self.current_menu = self.menu
                    self.menu=0
                    self.action=True
                    
                if text[cursor+1]==' ':
                    mylcd.lcd_display_string_pos(' ',1,cursor+1);
                    sleep(0.2)
                    mylcd.lcd_display_string_pos('_',1,cursor+1);
                    sleep(0.2)
                else:
                    mylcd.lcd_display_string_pos('*',1,cursor+1);
                    sleep(0.2)
                    mylcd.lcd_display_string_pos('_',1,cursor+1);
                    sleep(0.2)
                        
    
        


