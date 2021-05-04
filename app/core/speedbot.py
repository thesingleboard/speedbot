#!/usr/bin/env python
#import schedule
import settings
import time
import logging
from speedbot_lib import speedbot
from prom_lib import prometheus as prom
from lcd_lib import LCD as LCD16
from lcd_lib_2004 import LCD as LCD24
import liquidcrystal_i2c

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
        #this is a hack for now to test out this lcd library, may convert to usethis one.
        lcdcmd = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=4)
    elif settings.LCD_TYPE == 1602:
        lcd = LCD16()

    sb = speedbot()
    pr = prom()
    pr.start_server()



    while True:
        speedout = None
        #turn on the LCD
        try:
            lcdcmd.backlight()
        except Exception as e:
            logging.error(e)
            logging.error('Could not turn the lcd on.')

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

        #kill the packetloss not found issue, also in case var is empty
        if speedout:
            logging.info('Speedout is not empty.')
            for k,v in speedout.items():
                if k == 'packetloss' and isinstance(v,int) == False:
                    speedout['packetloss'] = 'N/A'
                elif k == 'packetloss' and isinstance(v,float) == True:
                    speedout['packetloss'] = speedout['packetloss'][:4]
        else:
            logging.info('Speedout is empty, filling in with 0.')
            #hack needs to recursivly redo if it fails
            speedout = {
                        'upload_Mbps':0.0000000,
                        'download_Mbps':0.0000000,
                        'packetloss':0.0000000,
                        'jitter':0.000000,
                        }

        try:
            lcd.clear()
            if settings.LCD_TYPE == 2004:
                logging.info('20x4 LCD in use.')
                lcd.message('Jitter: '+str(speedout['jitter']),3)
                lcd.message('PacketLoss: '+str(speedout['packetloss']),4)
                lcd.message('UP: '+str(speedout['upload_Mbps'])[:6]+' Mbps',1)
                lcd.message('Down: '+str(speedout['download_Mbps'])[:6]+' Mbps',2)
            elif settings.LCD_TYPE == 1604:
                logging.info('16x2 LCD in use.')
                lcd.message('UP: '+str(speedout['upload_Mbps'])[:6]+' Mbps',1)
                lcd.message('Down: '+str(speedout['download_Mbps'])[:6]+' Mbps',2)
        except Exception as e:
            print(e)
            logging.error('Could not display current speed.')

        try:
            time.sleep(settings.LCD_OFF)
            lcdcmd.noBacklight()
        except Exception as e:
            logging.error(e)
            logging.error('Could not turn off the lcd.')

        time.sleep(settings.INTERVAL)


if __name__ == '__main__':
    #Schedule is not working
    #schedule.every(settings.INTERVAL).minutes.do(speed())
    #while True:
     #   schedule.run_pending()
     #   time.sleep(1)
    
    main()
