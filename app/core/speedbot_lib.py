#!/usr/bin/env python
import subprocess
import os
import datetime
import settings
import logging
import ssl
import sqlite3
import psutil
import requests
import json
import paho.mqtt.client as paho

class speedbot():

    def __init__(self):
        #connect to the mqtt broker
        #self.client = paho.Client()
        #self.client.tls_set(settings.SSLCERTPATH+"/"+settings.SSLCERT,tls_version=ssl.PROTOCOL_TLSv1_2)
        #self.client.tls_insecure_set(True)

        try:
            #connect to the sqlite process
            self.sqlcon = sqlite3.connect(settings.DB_PATH+'iotDB.db')
            self.cursor = self.sqlcon.cursor()
        except Exception as e:
            logging.warn(e)
            logging.warn("Could not connect to the IOT sqlite DB.")

        try:
            self.cursor.execute('''CREATE TABLE speedbot (upload_Mbps text, download_Mbps text, packetloss text, timestamp text, location text, country text, testhost text)''')
        except Exception as e:
            logging.warn(e)
            logging.warn("Speedbot table already exists.")

        """
        try:
            self.client.connect(settings.MQTTBROKER, settings.MQTTPORT, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(e)
            logging.error("Could not connect to the MQTT Broker")
        """

    def get_hostname(self):
        """
        DESC: Get the hostname of the device
        INPUT: None
        OUTPUT:  hostname
        NOTE: None
        """
        out_array = []
        try:
            proc = subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True)
            (output, err) = proc.communicate()
            hostname = output.decode('utf-8').strip()
        except Exception as e:
            logging.error(e)
            logging.error("Could not get the hostname")

        return hostname

    def set_hostname(self, hostname=None):
        """
        DESC: Set the hostname of the speedbot
        INPUT: hostname
        OUTPUT: None
        NOTES: None
        """
        logging.info('Setting the system hostname.')
        
        if hostname == None:
            hostname = settings.HOSTNAME

        try:
            proc = subprocess.Popen("hostname %s"%hostname, stdout=subprocess.PIPE, shell=True)
            (output,err) = proc.communicate()
            out_array = output.decode('utf-8').strip().split()
            logging.info('Set the hostname to %s'%hostname)
        except Exception as e:
            logging.error(e)
            logging.error("Could not set the Speedbot hostname.")

        #Set the hostname permenately
        try:
            if os.path.exists('/etc/hostname'):
                logging.info('Removed the hostname file and rewrote with new hostname %s'%hostname)
                os.remove('/etc/hostname')
            else:
                loggin.warn('No /etc/hostname file')
        except Exception as e:
            logging.error(e)
            logging.error('Could not delete /etc/hostname file.')

        #Write the hostname
        try:
            new_file = open("/etc/hostname","w")
            new_file.write(hostname)
            new_file.close()
            logging.info('Wrote new hostname file.')
        except Exception as e:
            logging.error(e)
            logging.error("Could not create new hostname file.")

    def get_location(self, ext_ip):
        """
        DESC: Get the location of the speedbit based on the external IP
        INPUT: ext_ip - ip of the internet faceing IP
        OUTPUT: 
        NOTES: Get the external IP of the network(outward faceing NAT) from the check_speed function
        """
        try:
            output = requests.get("https://geolocation-db.com/json/ext_ip&position=true").json()
        except Exception as e:
            output = 'unknown'
            logging.error('Could not determin the location')

        return output

    def get_uptime(self):
        """
        DESC: Run get system uptime
        INPUT: None
        OUTPUT: out_dict - days
                         - hours
                         - minutes
                         - start_date
                         - start_time
        """
        up = True
        out_dict = {}
        try:
            uptime = subprocess.Popen("uptime -p", stdout=subprocess.PIPE, shell=True)
            (out, error) = uptime.communicate()
            out = out.decode("utf-8").rstrip().split()
        except Exception as e:
            logging.error("Could not get uptime %s: %s"%error, e)
            up = False

        try:
            since = subprocess.Popen("uptime -s", stdout=subprocess.PIPE, shell=True)
            (sout, serror) = since.communicate()
            sout = sout.decode("utf-8").rstrip().split()
        except Exception as e:
            logging.error("Could not get uptime %s: %s"%serror, e)
            up = False
            
        #make the out data useful
        if up:
            out_dict['uptime'] = out
            out_dict['start_date'] = sout[0]
            out_dict['start_time'] = sout[1]

        return out_dict

    def get_cpu_temp(self):
        #cat /etc/armbianmonitor/datasources/soctemp
        #/etc/update-motd.d/30-armbian-sysinfo
        """
        DESC: Get the cpu temperature in C or F
        INPUT: None
        OUTPUT:  out_dict - temp
                          - scale
        """
        raw = open("/etc/armbianmonitor/datasources/soctemp", "r")
        raw_temp = raw.read()
        temp = int(raw_temp.strip())/1000
        if settings.TEMP_SCALE == 'F':
            temp = temp * 9/5.0 + 32

        return {'temp':temp, 'scale':settings.TEMP_SCALE}

    def get_network_status(self, nic=None):
        """
        DESC: Get the netwotk transmit recieve on the selected nic.
        INPUT: nic - nic name
        OUTPUT: out_dict - recieve
                         - transmit
        """
        if nic is None:
            nic = settings.PHYSNET

        try:
            out = psutil.net_io_counters(pernic=True)
        except Exception as e:
            logging.error('Get network error: %s'%e)

        return out[nic]

    def get_system_memory(self):
        """
        DESC:  Get the system memory stats
        INPUT: None
        OUTPUT: out_dict - total_mem
                        - used_mem
                        - free_mem
                        - total_swap
                        - used_swap
                        - free_swap
        """
        out_dict = {}
        memory = {'total_mem':'$2', 'used_mem':'$3', 'free_mem':'$4'}
        for k, v in memory.items():
            try:
                logging.info("Getting the %s"%(k))
                raw = subprocess.Popen("free -hm | grep Mem | awk '{print %s}'"%(v), stdout=subprocess.PIPE, shell=True)
                (mout, merror) = raw.communicate()
                mout = mout.decode("utf-8").rstrip().split()
            except Exception as e:
                logging.error("Failed to get the %s"%(k))
                logging.error(e)
            out_dict['%s'%(k)] = mout[0]

        swap = {'total_swap':'$2', 'used_swap':'$3', 'free_swap':'$4'}
        for k, v in swap.items():
            try:
                logging.info("Getting the %s"%(k))
                raw = subprocess.Popen("free -hm | grep Swap | awk '{print %s}'"%(v), stdout=subprocess.PIPE, shell=True)
                (sout, serror) = raw.communicate()
                sout = sout.decode("utf-8").rstrip().split()
            except Exception as e:
                logging.error("Failed to get the %s"%(k))
                logging.error(e)
            out_dict['%s'%(k)] = sout[0]

        return out_dict

    def get_system_status(self):
        """
        DESC:  Return a system status overview
        INPUT: None
        OUTPUT: out_dict - hostname
                        - total_mem
                        - cpu_temp
                        - ip
                        - uptime
                        - node_id
        """
        hostname = self.get_hostname()
        cpu_temp = self.get_cpu_temp()
        mem = self.get_system_memory()
        ip = self.get_nic_ip_info(settings.PHYSNET)
        uptime = self.get_uptime()
        nodeid = self.get_node_id()

        return {'hostname':hostname,'cpu_temp':cpu_temp['temp'],'total_mem':mem['total_mem'],'ip':ip['ip'],'uptime':uptime,'node_id':nodeid}

####MQTT######
    '''
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
    '''

####DB####
    def db_insert(self,input_dict):
        """
        DESC: Insert the values in the sqlite DB
        INPUT: input_dict - upload_Mbps
                                      - download_Mbps
                                      - packetloss
                                      - timestamp
                                      - location
                                      - country
                                      - testhost
        OUTPUT: None
        NOTE: None
        """
        try:
            logging.info("Inserting speed info into db. %s"%(input_dict))
            self.cursor.execute("INSERT INTO speedbot VALUES ('"+input_dict['upload_Mbps']+"','"+input_dict['download_Mbps']+"','"+input_dict['packetloss']+"','"+input_dict['timestamp']+"','" + input_dict['location'] + "','"+input_dict['country']+"','"+input_dict['testhost']+"')")
            self.sqlcon.commit()
        except Exception as e:
            logging.error(e)
            logging.error("Could not insert data %s into the database"%(input_dict))

    def db_read(self):
        pass
    
    def db_purge(self):
        pass

####System#####
    def check_speed(self):
        #run the OOkla speed test.
        args = ['speedtest', '--accept-license', '-p', 'no', '-f', 'json']
        try:
            cmd = subprocess.Popen(args, stdout=subprocess.PIPE)
            output = json.loads(cmd.communicate()[0].decode("utf-8").rstrip())
        except Exception as e:
            logging.error("speedtest error: %s"%e)
            output = 'ERROR'

        #upload megabytes
        up = ((int(output['upload']['bytes']) * 8) / int(output['upload']['elapsed'])) /1000

        #download megabytes
        down = ((int(output['download']['bytes']) * 8) / int(output['download']['elapsed'])) /1000

        try:
            self.db_insert({'upload_Mbps':str(up),
                                      'download_Mbps':str(down),
                                      'packetloss':str(output['packetLoss']),
                                      'timestamp':str(output['timestamp']),
                                      'location':str(output['server']['location']),
                                      'country':str(output['server']['country']),
                                      'testhost':str(output['server']['host'])
                                      })
            logging.info("Inserted speed info into Speedbot DB.")
        except Exception as e:
            logging.error("could not insert ")

        logging.info({'timestamp':output['timestamp'],'upload_Mbps':up,'download_Mbps':down,'location':output['server']['location'],'country':output['server']['country'],'testhost':output['server']['host'],'packetloss':output['packetLoss']})
        return {'timestamp':output['timestamp'], 'external_ip':output['interface']['externalIp'], 'upload_Mbps':up, 'download_Mbps':down, 'server_location':output['server']['location'], 'country':output['server']['country'], 'testhost':output['server']['host'], 'packetloss':output['packetLoss']}

    def write_config(self):
        pass