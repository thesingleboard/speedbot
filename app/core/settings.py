#!/usr/bin/env python
import os
import socket
import time
import calendar

#api version
API = '0.1Alpha'

#hostname
HOSTNAME = socket.gethostname()

#The GPIO pins to use for sensors
PINS = os.getenv('PINS',None)
#Take comma seperated string and turn into list so it can be used.
PINS = PINS.split(',')

#The time interval
INTERVAL = os.getenv('INTERVAL',3600)
INTERVAL = int(INTERVAL)

#physical network name wlan0 or eth0
PHYSNET = os.getenv('PHYSNET','eth0')

#DB directory
DB_PATH = os.getenv('DB_PATH','/opt/speedbot-data/')
PROM_PORT = int(os.getenv('PROM_PORT','9002'))

#get the epoc time 
STARTOFTIME = calendar.timegm(time.gmtime())

TEMP_SCALE = os.getenv('TEMP_SCALE','F')

# 1602 is 16 wide 2 high
# 2004 is 20 wide 4 high
LCD_TYPE = 2004

#LCD_ADDR = 0x33
LCD_ADDR = 0x27

#Turn LCD off aftr 5 seconds
LCD_OFF = os.getenv('LCD_OFF',5)

#mgtt broker host, IP or URL
#MQTTBROKER = os.getenv('MQTTBROKER',None)

#MQTTPORT = os.getenv('MQTTPORT',None)
#MQTTPORT = int(MQTTPORT)

#SSLCERTPATH = os.getenv('SSLCERTPATH',None)

#SSLCERT = os.getenv('SSLCERT',None)

CONFIG = {  'API':API,
            'HOSTNAME':HOSTNAME,
            'PINS':PINS,
            'INTERVAL':INTERVAL,
            'STARTOFTIME':STARTOFTIME,
            'LCD_ADDR':LCD_ADDR,
            'TEMP_SCALE':TEMP_SCALE,
            'LCD_OFF':LCD_OFF,
            'LCD_TYPE':LCD_TYPE,
            'PHYSNET':PHYSNET,
            'PROM_PORT':PROM_PORT,
            
            #'MQTTBROKER':MQTTBROKER,
            #'MQTTPORT':MQTTPORT,
            #'SSLCERTPATH':SSLCERTPATH,
            #'SSLCERT':SSLCERT, 
            }
