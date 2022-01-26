import os
import threading
from collections import namedtuple
#import time
from Sources.UI import Keys, ActionMenu#, Clock

# agregar tiempo de espera para la carga del sistema
#print("Esperando carga del sistema")
#time.sleep(10)

# obtener listado de tarjetas de audio
rec = os.popen('arecord -l | grep card').read()

# dividir el string por número de tarjeta
rec = rec.split('card ')

# obtener numero de cada tarjeta
b1 = int(rec[1][0])
b2 = int(rec[2][0])
b3 = int(rec[3][0])
b4 = int(rec[4][0])
#print("Numeros de tarjetas")
#print(b1)
#print(b2)
#print(b3)
#print(b4)

# obtener listado de dispositivos usb
usb_r = os.popen('lsusb').read()

# dividir el string por número de Dispositivo
usb_r = usb_r.split('Device ')

# Obtener número de cada dispositivo
a1 = int(usb_r[4][2])
a2 = int(usb_r[3][2])
a3 = int(usb_r[2][2])
a4 = int(usb_r[1][2])
#print("Numeros de dispositivo")
#print(a1)
#print(a2)
#print(a3)
#print(a4)

# Partiendo de que tenemos dos grupos de datos:
# 1. Núm de Device + el orden de puerto   (index, usb)
# 2. Los números de las tarjetas de audio (hw)

# se crea una named tuple
Cards = namedtuple('Cards', 'index usb hw')

cards = []
# Se agregan los num de dispositivo y el índice
cards.append(Cards(index=1, usb=a1, hw=0))
cards.append(Cards(index=2, usb=a2, hw=0))
cards.append(Cards(index=3, usb=a3, hw=0))
cards.append(Cards(index=4, usb=a4, hw=0))

# Se ordena el arreglo de acuerdo a los num de dispositivo
cards.sort(key=lambda x: getattr(x,'usb'))

# Se agregan los números de tarjeta de acuerdo al nuevo orden
cards[0] = Cards(index=cards[0].index, usb=cards[0].usb, hw=b1)
cards[1] = Cards(index=cards[1].index, usb=cards[1].usb, hw=b2)
cards[2] = Cards(index=cards[2].index, usb=cards[2].usb, hw=b3)
cards[3] = Cards(index=cards[3].index, usb=cards[3].usb, hw=b4)

# Se ordena el arreglo nuevamente de acuerdo al índice
cards.sort(key=lambda x: getattr(x, 'index'))

# Se genera el texto .asoundrc son los números de las tarjetas en el orden actual
# crear archivo .asoundrc (esto implica que el script se debe ejecutar en el home)
os.popen('touch .asoundrc')

# abrir el archivo
file = open('.asoundrc', 'w')
#print("Creando archivo .asoundrc")

# Escribir archivo
file.write("pcm.multitrack {\n")
file.write(" type multi;\n")
file.write(" slaves.a.pcm hw:" + str(cards[0].hw) + "\n")
file.write(" slaves.a.channels 1;\n")
file.write(" slaves.b.pcm hw:" + str(cards[1].hw) + "\n")
file.write(" slaves.b.channels 1;\n")
file.write(" slaves.c.pcm hw:" + str(cards[2].hw) + "\n")
file.write(" slaves.c.channels 1;\n")
file.write(" slaves.d.pcm hw:" + str(cards[3].hw) + "\n")
file.write(" slaves.d.channels 1;\n")
file.write(" bindings.0.slave a;\n")
file.write(" bindings.0.channel 0;\n")
file.write(" bindings.1.slave b;\n")
file.write(" bindings.1.channel 0;\n")
file.write(" bindings.2.slave c;\n")
file.write(" bindings.2.channel 0;\n")
file.write(" bindings.3.slave d;\n")
file.write(" bindings.3.channel 0;\n}")

file.close()
#print("archivo .asoundrc creado")

#ck = Clock()
#ck.start()

menu = ActionMenu()
menu.start()

#key_read = Keys()
#key_read.start()
