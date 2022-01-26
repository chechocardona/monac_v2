import RPi_I2C_driver

from datetime import datetime
from time import sleep, mktime, strftime

fontdata = [
        # Char 0 - left arrow
        [ 0x1,0x3,0x7,0xf,0xf,0x7,0x3,0x1],
        # Char 1 - right arrow
        [ 0x10,0x18,0x1c,0x1e,0x1e,0x1c,0x18,0x10]
]

mylcd = RPi_I2C_driver.lcd()
mylcd.lcd_clear()
dti = mktime(datetime.now().timetuple())-datetime.now().timetuple().tm_sec # para sincronizar los segundos
mylcd.lcd_display_string_pos(datetime.now().strftime('%d/%m/%y %H:%M'),1,1)
#mylcd.lcd_load_custom_chars(fontdata)
#mylcd.lcd_display_string_pos(chr(0),2,1)
#mylcd.lcd_display_string_pos(chr(1),2,2)
while 1:
 ndti = mktime(datetime.now().timetuple())
 if dti+59 < ndti: # cambia cada minuto
  dti = ndti
  mylcd.lcd_clear()
  mylcd.lcd_display_string_pos(datetime.now().strftime('%d/%m/%y %H:%M'),1,1)
  sleep(0.95)
 else:
  sleep(0.01)
