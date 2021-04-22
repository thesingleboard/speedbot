#!/usr/bin/env python
#import schedule
import settings
import time
import logging
from speedbot_lib import speedbot
from prom_lib import prometheus as prom
from lcd_lib import LCD as LCD16
from lcd_lib_2004 import LCD as LCD24

def turn_off_lcd():
    pass

def main():
    """
    DESC: Main method
    INPUT: None
    OUTPUT: None
    NOTE: None
    """
    lcd = None
    if settings.LCD_TYPE == 2004:
        lcd = LCD24()
    elif settings.LCD_TYPE == 1602:
        lcd = LCD16()

    sb = speedbot()
    pr = prom()
    pr.start_server()
    
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

        #emit prom
        try:
            logging.info("Emiting Prometheus metrics.")
            pr.network_speed({'upload':int(speedout['upload_Mbps']),'download':int(speedout['download_Mbps'])})
        except Exception as e:
            logging.error(e)

        #kill the packetloss not found issue
        for k,v in speedout.items():
            if k == 'packetloss' and isinstance(v,int) == False:
                speedout['packetloss'] = 'N/A'
            elif k == 'packetloss' and isinstance(v,float) == True:
                speedout['packetloss'] = speedout['packetloss'][:4]

        try:
            lcd.clear()
            #cut off everything after the decimal since it is a float
            #iu = int(speedout['upload_Mbps'])
            #idown = int(speedout['download_Mbps'])
            if settings.LCD_TYPE == 2004:
                lcd.message('Jitter: '+str(speedout['jitter']),3)
                lcd.message('PacketLoss: '+str(speedout['packetloss']),4)
                lcd.message('UP: '+str(speedout['upload_Mbps'])[:6]+' Mbps',1)
                lcd.message('Down: '+str(speedout['download_Mbps'])[:6]+' Mbps',2)
            elif settings.LCD_TYPE == 1604:   
                lcd.message('UP: '+str(speedout['upload_Mbps'])[:6]+' Mbps',1)
                lcd.message('Down: '+str(speedout['download_Mbps'])[:6]+' Mbps',2)
        except Exception as e:
            print(e)
            logging.error('Could not display current speed.')

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
    
    main()
