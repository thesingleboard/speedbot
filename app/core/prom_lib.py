import os
import settings
import logging
from prometheus_client import start_http_server
from prometheus_client import Gauge

class prometheus():
    def __init__(self):
        """
        DESC: Initialize 
        INPUT: 
        OUTPUT: None
        NOTE: None
        """
        logging.info("Starting Prometheus scrape endpoint.")
        #simple internal http server used as a scrape endpoint.
        #try:
        #except Exception as e:
        #    logging.error(e)
        #    logging.error("Could not start Prometheus scrape endpoint.")
        
    def start_server(self):
        start_http_server(9002)
        self.used_mem = Gauge('speedbot_used_memory', 'Speedbot Used Memory')
        self.free_mem = Gauge('speedbot_free_memory', 'Speedbot Free Memory')
        self.upload_speed = Gauge('speedbot_upload_in_Mbps', 'Upload speed in Mbps')
        self.download_speed = Gauge('speedbot_download_in_Mbps', 'Download speed in Mbps')
        self.packetloss = Gauge('speedbot_packetloss', 'Packet loss')
        self.jitter = Gauge('speedbot_jitter', 'jitter')
    
    def network_spec(self,input_dict):
        """
        DESC: Emit the used and free memory
        INPUT: input_dict - packetloss
                          - jitter
        OUTPUT: None
        NOTE: This is a Gauge
        """
        try:
            logging.info("Emitting network packetloss.")
            self.packetloss.set(input_dict['packetloss'])
        except Exception as e:
            logging.error(e)
            logging.error("Could not emit the network packetloss.")
            
        try:
            logging.info("Emitting network jitter.")
            self.jitter.set(input_dict['jitter'])
        except Exception as e:
            logging.error(e)
            logging.error("Could not emit the network jitter.")
        
        
    def memory(self,input_dict):
        """
        DESC: Emit the used and free memory
        INPUT: input_dict - free
                          - used
        OUTPUT: None
        NOTE: This is a Gauge
        """
        try:
            logging.info("Emitting the used memory.")
            self.used_mem.set(input_dict['used'])
        except Exception as e:
            logging.warn(e)
            logging.warn("Could not gauge used memory.")
        
        try:
            logging.info("Emitting the free memory.")
            self.free_mem.set(input_dict['free'])
        except Exception as e:
            logging.warn(e)
            logging.warn("Could not gauge free memory.")
        
    def network_speed(self,input_dict):
        """
        DESC: Emit the upload and download speed measured by the speedbot.
        INPUT: input_dict - upload
                          - download
        OUTPUT: None
        NOTE: This is a Gauge
        """
        try:
            logging.info("Emitting upload speed.")
            self.upload_speed.set(input_dict['upload'])
        except Exception as e:
            logging.warn(e)
            logging.warn("Could not gauge upload speed.")
        
        try:
            logging.info("Emitting download speed.")
            self.download_speed.set(input_dict['download'])
        except Exception as e:
            logging.warn(e)
            logging.warn("Could not gauge download speed.")