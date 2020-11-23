#!/usr/local/bin/python
import os
import schedule
import subprocess
import settings

def check_speed():
    pass

def main():
    #get the LCD up and running
    

if __name__ == '__main__':
    #Run the function
    schedule.every(settings.INTERVAL).seconds.do(main())
    while True:
        schedule.run_pending()

#echo 'YES' | speedtest --progress=no human-readable -f json