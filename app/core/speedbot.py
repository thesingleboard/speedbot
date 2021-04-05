#!/usr/bin/env python
#import schedule
import settings
import time
import logging

#from lcd_lib import LCD
from lcd_lib_2004 import LCD
from speedbot_lib import speedbot
from prometheus_client import Gauge, start_http_server

def turn_off_lcd():
    pass

def main():
    """
    DESC: Main method
    INPUT: None
    OUTPUT: None
    NOTE: None
    """
    lcd = LCD()
    sb = speedbot()
    upload = Gauge('upload_in_Mbps', 'Upload speed in Mbps')
    download = Gauge('download_in_Mbps', 'Download speed in Mbps')
    
    while True:
        speedout = None
        #turn on the LCD
        #try:
        #    lcd.lcdon()
        #except Exception as e:
        #    logging.error(e)
         #   logging.error('Could not turn the lcd on.')

        try:
            #clear everything 
            lcd.clear()
            lcd.message('Checking Speed',1)
            lcd.message('One Moment...',2)
        except Exception as e:
            logging.error('Could not display status: %s'%(e))

        try:
            speedout = sb.check_speed()
        except Exception as e:
            logging.error('Could not calculate the speed: %s'%(e))

        try:
            lcd.clear()
            #cut off everything after the decimal since it is a float
            iu = int(speedout['upload_Mbps'])
            id = int(speedout['download_Mbps'])
            lcd.message('UP: '+str(iu)+' Mbps',1)
            lcd.message('Down: '+str(id)+' Mbps',2)
        except Exception as e:
            print(e)
            logging.error('Could not display current speed.')

        upload.set(iu)
        download.set(id)
        #try:
        #    time.sleep(settings.LCD_OFF)
        #    lcd.lcdoff()
        #except Exception as e:
        #    logging.error(e)
        #    logging.error('Could not turn off the lcd.')

        time.sleep(settings.INTERVAL)


if __name__ == '__main__':
    #Schedule is not working
    #schedule.every(settings.INTERVAL).minutes.do(speed())
    #while True:
     #   schedule.run_pending()
     #   time.sleep(1)
    start_http_server(settings.PROM_PORT)
    main()
