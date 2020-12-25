#!/usr/bin/env python
import subprocess
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
        """
        self.client = paho.Client()
        self.client.tls_set(settings.SSLCERTPATH+"/"+settings.SSLCERT,tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.tls_insecure_set(True)
        """

        try:
            #connect to the sqlite process
            self.sqlcon = sqlite3.connect(settings.DB_PATH+'iotDB.db')
            self.cursor = self.sqlcon.cursor()
        except Exception as e:
            logging.warn(e)
            logging.warn("Could not connect to the IOT sqlite DB.")
            
        try:
            self.cursor.execute('''CREATE TABLE speedbot (upload real, download real, packetloss integer, timestamp text, location text, country text, testhost text)''')
        except Exception as e:
            logging.info(e)
            logging.warn("Speedbot table already exists.")

        """
        try:
            self.client.connect(settings.MQTTBROKER, settings.MQTTPORT, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(e)
            logging.error("Could not connect to the MQTT Broker")
        """

    def list_nics(self):
        """
        DESC: List the available nics
        INPUT: None
        OUTPUT: out_array - list of nics
        DESC: None
        """
        out_array = []
        try:
            proc = subprocess.Popen("sudo ls -I br* -I lo -I vir* /sys/class/net/", stdout=subprocess.PIPE, shell=True)
            (output,err) = proc.communicate()
            out_array = output.decode('utf-8').strip().split()
        except Exception as e:
            logging.error(e)
            logging.error("Could not get the list of nics")

        return out_array

    def get_nic_ip_info(self,nic):
        """
        DESC: Get the IP of the primary nic
        INPUT: nic - the name of the primary nic
        OUTPUT out_dict - ip
                        - gateway
        NOTES: None
        """
        try:
            proc = subprocess.Popen("ip addr | grep '%s' -A2 | grep 'inet' | head -1 | awk '{print $2}' | cut -f1  -d'/'"%nic, stdout=subprocess.PIPE, shell=True)
            (output,err) = proc.communicate()
            ip = str(output.decode('utf-8').strip())
        except Exception as e:
            ip = e

        try:
            proc2 = subprocess.Popen("/sbin/ip route | awk '/default/ { print $3 }'", stdout=subprocess.PIPE, shell=True)
            (output2,err2) = proc2.communicate()
            gateway = str(output2.decode('utf-8').strip())
        except Exception as e:
            gateway = e

        return {'ip':ip,'gateway':gateway}

    def get_location(self,ext_ip):
        """
        DESC: Get the location of the speedbit based on the external IP
        INPUT: ext_ip - ip of the internet faceing IP
        OUTPUT: 
        """
        try:
            output = requests.get("https://geolocation-db.com/json/%s&position=true"%(ext_ip).json())
        except Exception as e:
            output = 'unknown'
            logging.error('Could not determin the location')

        return output

    def get_node_id(self):
        """
        DESC: Get the system ID and use it as the unchangebale node id.
        INPUT: None
        OUTPUT: node_id
        """
        # Extract serial from cpuinfo file
        node_id = "000-00000000-00000"
        try:
            f = open('/etc/nodeid','r')
            for line in f:
                    node_id = line
            f.close()
        except:
            node_id = "ERROR000000000"

        return device_id

    def get_mac(self,nic):
        """
        DESC: return the MAC(serial) of the first ethernet adapter used to identify the system.
        """
        mac = '00:00:00:00:00:00'
        try:
            proc = subprocess.Popen("ip addr | grep '%s' -A2 | grep 'link/ether' | head -1 | awk '{print $2}' | cut -f1  -d'/'"%nic, stdout=subprocess.PIPE, shell=True)
            (output,err) = proc.communicate()
            mac = output.decode("utf-8").strip()
        except Exception as e:
            mac = e

        return mac

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
            uptime = subprocess.Popen("uptime -p",stdout=subprocess.PIPE,shell=True)
            (out,error) = uptime.communicate()
            out = out.decode("utf-8").rstrip().split()
        except Exception as e:
            logging.error("Could not get uptime %s: %s"%error,e)
            up = False

        try:
            since = subprocess.Popen("uptime -s",stdout=subprocess.PIPE,shell=True)
            (sout,serror) = since.communicate()
            sout = sout.decode("utf-8").rstrip().split()
        except Exception as e:
            logging.error("Could not get uptime %s: %s"%serror,e)
            up = False
            
        #make the out data useful
        if(up):
            out_dict['days'] = out[1]
            out_dict['hours'] = out[3]
            out_dict['minutes'] = out[5]
            out_dict['start_date'] = sout[0]
            out_dict['start_time'] = sout[1]

        return out_dict

    #def get_cpu_status(self):
    #    """
    #    DESC: Run the vcgencmd command and get some systme level stats
    #    INPUT: None
    #    OUTPUT: out_dict - cpu_count
    #                     - cpu_temp
    #                     - cpu_volts
    #                     - ram_volts
    #                     - io_volts
    #                     - phy_volts
    #    """
    #    cmds = {'cpu_temp':'measure_temp','cpu_volts':'measure_volts core','ram_volts':'measure_volts sdram_c','io_volts':'measure_volts sdram_i','phy_volts':'measure_volts sdram_p','cpu_clock':'measure_clock arm'}
    #    output= {}
    #    output['cpu_count'] = psutil.cpu_count()

    #    for k,v in cmds.items():
    #        args = ['vcgencmd']
    #        args.append(v)
    #        try:
    #            cmd = subprocess.Popen(args, stdout=subprocess.PIPE)
    #            out = cmd.communicate()[0].decode("utf-8").rstrip().split('=')
    #            output[k] = out[1]
    #        except Exception as e:
    #            logging.error("vcgencmd: %s"%e)
    #            output[k] = 'ERROR'

    #    return output

    def get_network_status(self,nic=None):
        """
        DESC: Get the netwotk transmit recieve on the selected nic.
        INPUT: nic - nic name
        OUTPUT: out_dict - recieve
                         - transmit
        """
        if(nic is None):
            nic = settings.PHYSNET

        try:
            out = psutil.net_io_counters(pernic=True)
        except Exception as e:
            logging.error('Get network error: %s'%e)

        return out[nic]

    #def get_memory(self):
    #    """
    #    DESC:  Get the cpu and gpu memory
    #    INPUT: None
    #    OUTPUT: out_dict - cpu_type
    #                     - cpu_mem
    #                     - gpu_mem
    #    """
    #    cmds = {'cpu_mem':'arm','gpu_mem':'gpu'}
    #    output = {}
    #    for k,v in cmds.items():
    #        args = ['vcgencmd','get_mem']
    #        args.append(v)
    #        try:
    #            cmd = subprocess.Popen(args, stdout=subprocess.PIPE)
    #            output[k] = cmd.communicate()[0].decode("utf-8").rstrip()
    #        except Exception as e:
    #            logging.error("vcgencmd: %s"%e)
    #            output[k] = 'ERROR'

    #    return output

    #def get_system_status(self):
        """
        DESC: Get the system status metrics from the device.
        INPUT: None
        OUTPUT: out_dict - cpu_id
                       - cpu_temp
                       - cpu_voltage
                       - cpu_clock
                       - system_memory
                       - system_uptime
                       - network_tx_stats
                       - network_rx_stats
        """
     #   cpu_stats = self.get_cpu_status()
     #   system_mem = self.get_memory()
     #   uptime = self.get_uptime()
     #   network = self.get_network_status()

     #   memory = system_mem['cpu_mem'].split('=')

     #   return {'cpu_id':self.get_cpu_id(),
     #               'cpu_temp':cpu_stats['cpu_temp'],
     #               'cpu_voltage':cpu_stats['cpu_volts'],
     #               'cpu_clock':cpu_stats['cpu_clock'],
     #               'system_memory':memory[1],
     #               'system_uptime':uptime['days']+" days "+uptime['minutes']+" minutes",
     #               'network_bytes_sent': network.bytes_sent,
     #               'network_bytes_recv': network.bytes_recv
     #               }

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
####DB#######
    def prune_db():
        pass

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
        #speedbot (upload real, download real, packetloss integer, timestamp text, location text, country text, testhost text)''
        out = True
        try:
            logging.info("Inserting speed info into db. %s"%(input_dict))
            self.cursor.execute("INSERT INTO speedbot VALUES ('"+float(input_dict['upload_Mbps'])+"','"+float(input_dict['download_Mbps'])+"','"+int(input_dict['packetloss'])+"','"+str(input_dict['timestamp'])+"','" + str(input_dict('location')) + "','"+str(input_dict['country'])+"','"+str(input_dict['testhost'])+"')")
            self.sqlcon.commit()
        except Exception as e:
            out = False
            logging.error(e)
            logging.error("Could not insert data %s into the database"%(input_dict)

    def db_fetch(self,sql_query):
        """
        DESC: Read specific info from the onboard DB.
        INPUT: sql_query
        OUTPUT: None
        NOTE: None
        """
        #sql_query = Select * from speedbot where location='timestamp'
        pass
    
    def db_fetch_all(self):
        """
        DESC: Read all info from the DB.
        INPUT: None
        OUTPUT: Dictionary of quries
        NOTE: None
        """
        pass

    def delete_record():
        pass

####System#####
    def check_speed(self):
        #run the OOkla speed test.
        args = ['speedtest', '--accept-license' ,'-p', 'no', '-f' ,'json']
        try:
            cmd = subprocess.Popen(args, stdout=subprocess.PIPE)
            output = json.loads(cmd.communicate()[0].decode("utf-8").rstrip())
        except Exception as e:
            logging.error("speedtest error: %s"%e)
            output = 'ERROR'

        #import pprint
        #pprint.pprint(output)

        #upload megabytes
        up = ((int(output['upload']['bytes']) * 8) / int(output['upload']['elapsed'])) /1000

        #download megabytes
        down = ((int(output['download']['bytes']) * 8) / int(output['download']['elapsed'])) /1000

        try:
            #dbInsert
        except Exception as e:
            logging.error("could not insert ")
            
        logging.info({'timestamp':output['timestamp'],'upload_Mbps':up,'download_Mbps':down,'location':output['server']['location'],'country':output['server']['country'],'testhost':output['server']['host'],'packetloss':output['packetLoss']})
        return {'timestamp':output['timestamp'],'external_ip':output['interface']['externalIp'],'upload_Mbps':up,'download_Mbps':down,'server_location':output['server']['location'],'country':output['server']['country'],'testhost':output['server']['host'],'packetloss':output['packetLoss']}

    def write_config(self):
        pass