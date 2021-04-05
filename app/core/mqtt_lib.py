import os
import json
import paho.mqtt.client as paho

class MQTT():

    def __init__(self):
        #connect to the mqtt broker
        #self.client = paho.Client()
        #self.client.tls_set(settings.SSLCERTPATH+"/"+settings.SSLCERT,tls_version=ssl.PROTOCOL_TLSv1_2)
        #self.client.tls_insecure_set(True)
        

     """
        try:
            self.client.connect(settings.MQTTBROKER, settings.MQTTPORT, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(e)
            logging.error("Could not connect to the MQTT Broker")
        """

    def send_data_mqtt(self,input_dict):
        """
        DESC: send the sensor readings to the MQTT server
        INPUT: input_dict - sensor
                          - temp
                          - scale - F/C
                          - humidity
        OUTPUT: None
        NOTE: None
        """
        #send a mesage to the MQTT broker, pub
        try:
            self.client.publish(settings.HOSTNAME+"/"+input_dict['sensor']+"/temperature",str(input_dict['temp'])+""+input_dict['scale'])
            self.client.publish(settings.HOSTNAME+"/"+input_dict['sensor']+"/humidity",str(input_dict['humidity']))
        except Exception as e:
            logging.error(e)
            logging.error("Could not send messages to MQTT broker")

    def send_status_mqtt(self,input_dict):
        """
        DESC: send the device status to the MQTT server
        INPUT: input_dict - cpu_id
                          - cpu_temp
                          - cpu_voltage
                          - cpu_clock
                          - system_memory
                          - system_uptime
                          - network_tx_stats
                          - network_rx_stats
        OUTPUT: None
        NOTE: None
        """

        try:
            self.client.publish(settings.HOSTNAME+"/"+input_dict['cpu_id']+"/status",input_dict)
        except Exception as e:
            logging.error(e)
            logging.error("Could not send messages to MQTT broker")

    def recieve_mqtt(self,input_array):
        """
        INPUT: input_array - array of topics to subscribe to.
        """
        #get a message from the MQTT broker, sub 
        self.subscribe(input_array)