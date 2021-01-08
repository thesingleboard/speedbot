import subprocess
import os

class systemFunctions():
    #docker lib 4.4.1
    #pip install docker=='4.4.1'
    def __init__(self):
        config = open('/etc/speedbot.cfg','r')
        self.out_config = {}
        for c in config:
            if c[:6] == 'export':
                raw = str(c[7:]).split('=')
                #build a config dictionary
                self.out_config[raw[0]] = raw[1][:-1]
            else:
                continue
        self.docker_client = docker.from_env()

    def update_speedbot_container(self):
         try:
            
        except Exception as e:
            logging.error(e)
            logging.error("Could not set the Speedbot hostname.")

    def factory_reset_speedbot_container(self):
        pass
    
    def restart_speedbot_container(self):
        pass
    
    def stop_speedbot_container(self):
        pass
    
    def start_speedbot_container(self):
        pass
    
    def update_device_ip(self):
        pass