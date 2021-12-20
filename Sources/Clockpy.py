import RPi_I2C_driver

from datetime import datetime
from time import sleep, mktime, strftime

mylcd = RPi_I2C_driver.lcd()
mylcd.lcd_clear()
dti = mktime(datetime.now().timetuple())
mylcd.lcd_display_string_pos(datetime.now().strftime('%b %d  %H:%M'),1,1)
mylcd.lcd_display_string_pos("Presiona 'A'",2,2)
while 1:
    ndti = mktime(datetime.now().timetuple())
    if dti+59 < ndti: # cambia cada minuto pero no está sincronizado con los segundos
        dti = ndti
        mylcd.lcd_clear()
        mylcd.lcd_display_string_pos(datetime.now().strftime('%b %d  %H:%M'),1,1)
        sleep(0.95)
    else:
        sleep(0.01)