#!/usr/bin/env python
import os
import socket
import time
import calendar

#api version
API = os.getenv('API',None)

#hostname
HOSTNAME = socket.gethostname()

#The GPIO pins to use for sensors
PINS = os.getenv('PINS',None)
#Take comma seperated string and turn into list so it can be used.
PINS = PINS.split(',')

#The time interval
INTERVAL = os.getenv('INTERVAL',10)
INTERVAL = int(INTERVAL)

#physical network name wlan0 or eth0
PHYSNET = os.getenv('PHYSNET',None)

#DB directory
DB_PATH = os.getenv('DB_PATH','/opt/speedbot-data/')

#mgtt broker host, IP or URL
#MQTTBROKER = os.getenv('MQTTBROKER',None)

#MQTTPORT = os.getenv('MQTTPORT',None)
#MQTTPORT = int(MQTTPORT)

#SSLCERTPATH = os.getenv('SSLCERTPATH',None)

#SSLCERT = os.getenv('SSLCERT',None)

#get the epoc time 
STARTOFTIME = calendar.timegm(time.gmtime())

TEMP_SCALE = os.getenv('TEMP_SCALE','F')

LCD_ADDR = 0x3f

CONFIG = {  'API':API,
            'HOSTNAME':HOSTNAME,
            'PINS':PINS,
            'INTERVAL':INTERVAL,
            #'MQTTBROKER':MQTTBROKER,
            #'MQTTPORT':MQTTPORT,
            #'SSLCERTPATH':SSLCERTPATH,
            #'SSLCERT':SSLCERT,
            'STARTOFTIME':STARTOFTIME,
            'LCD_ADDR':LCD_ADDR,
            'TEMP_SCALE':TEMP_SCALE
            }