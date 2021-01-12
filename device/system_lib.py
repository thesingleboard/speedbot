import subprocess
import docker
import json
import logging
import os

class dockerFunctions():
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
        #trying out the docker API lib
        self.docker_client = docker.from_env()

    #atomic Docker functions
    def _docker_pull_new_speedbot(self,image,version=None):
        if version == None:
            version = stable
        try:
            self.docker_client.images.pull(image+':'+version)
        except Exception as e:
            logging.error(e)
            logging.error('Could not pull %s:%s'%image,version)

    def _docker_stop_speedbot(self,remove=False):
        args = ['docker', 'stop', 'speedbot']
        try:
            cmd = subprocess.Popen(args, stdout=subprocess.PIPE)
            output = json.loads(cmd.communicate()[0].decode("utf-8").rstrip())
            logging.info('Stopped the speedbot container.')
        except Exception as e:
            logging.error(e)
            logging.error('Could not stop the speedbot container.')
    
        if remove is True:
            args = ['docker', 'rm', 'speedbot']
            try:
                cmd = subprocess.Popen(args, stdout=subprocess.PIPE)
                output = json.loads(cmd.communicate()[0].decode("utf-8").rstrip())
                logging.info('Removed the speedbot container.')
            except Exception as e:
                logging.error(e)
                logging.error('Could not remove the speedbot container')

    def _docker_start_speedbot(self):
        try:
            proc = subprocess.Popen("docker run -d -h speedbot --network=host --privileged -p 10500:10500 -v /opt/speedbot-data:/opt/speedbot-data \
                                    --name speedbot -e PINS=%s -e INTERVAL=%s -e MQTTBROKER=%s -e MQTTPORT=%s -e API=%s speedbot:%s"
                                    %(self.out_config['PINS'],self.out_config['INTERVAL'],self.out_config['MQTTBROKER'],self.out_config['MQTTPORT'],
                                      self.out_config['API'],self.out_config['VERSION']),
                                    stdout=subprocess.PIPE, shell=True)
            (output, err) = proc.communicate()
            mac = output.decode("utf-8").strip()
            logging.info('Starting the new speedbot container.')
        except Exception as e:
            logging.error(e)
            logging.error('Could not start the new speedbot container.')

    #specifc operations
    def update_speedbot_container(self):
        try:
            #pull the new container
            self._docker_pull_new_speedbot('speedbot','latest')
        except Exception as e:
            logging.error(e)
            logging.error("Could not pull the speedbot container.")
        
        try:
            #stop the old container
            self._docker_stop_speedbot(True)
        except Exception as e:
            logging.error(e)
            logging.error("The speedbot container failed to stop.")
        
        try:
            #pull the new container
            self._docker_start_speedbot()
        except Exception as e:
            logging.error(e)
            logging.error("Could not pull the speedbot container.")

    def factory_reset_speedbot_container(self):
        pass
    
    def restart_speedbot_container(self):
        pass
    
    def stop_speedbot_container(self):
        pass
    
    def start_speedbot_container(self):
        pass

class systemFunctions:
    
    def __init__(self):
        pass
    
    def get_node_id(self):
        """
        DESC: Get the system ID and use it as the unchangebale node id.
        INPUT: None
        OUTPUT: node_id
        """
        # Extract serial from cpuinfo file
        node_id = "000-00000000-00000"
        try:
            f = open('/etc/nodeid', 'r')
            for line in f:
                node_id = line.strip()
            f.close()
        except Exception as e:
            logging.error(e)
            node_id = "ERROR000000000"

        logging.info('Returned node id %s.'%node_id)

        return node_id

    def get_mac(self, nic):
        """
        DESC: return the MAC(serial) of the first ethernet adapter used to identify the system.
        """
        mac = '00:00:00:00:00:00'
        try:
            proc = subprocess.Popen("sudo ip addr | grep '%s' -A2 | grep 'link/ether' | head -1 | awk '{print $2}' | cut -f1  -d'/'"%nic, stdout=subprocess.PIPE, shell=True)
            (output, err) = proc.communicate()
            mac = output.decode("utf-8").strip()
        except Exception as e:
            logging.error(e)
            logging.error('Could not find the nic mac.')

        logging.info('Returned the mac %s'%mac)

        return mac

    def get_nic_ip_info(self, nic):
        """
        DESC: Get the IP of the primary nic
        INPUT: nic - the name of the primary nic
        OUTPUT out_dict - ip
                        - gateway
        NOTES: None
        """
        
        ip = '0.0.0.0'
        try:
            proc = subprocess.Popen("sudo ip addr | grep '%s' -A2 | grep 'inet' | head -1 | awk '{print $2}' | cut -f1  -d'/'"%nic, stdout=subprocess.PIPE, shell=True)
            (output, err) = proc.communicate()
            ip = str(output.decode('utf-8').strip())
        except Exception as e:
            logging.error(e)

        logging.info('Returned the ip %s'%ip)

        cidr = None
        try:
            proc3 = subprocess.Popen("sudo ip addr | grep '%s' -A2 | grep 'inet' | head -1 | awk '{print $2}' | cut -f2  -d'/'"%nic, stdout=subprocess.PIPE, shell=True)
            (output3, err3) = proc3.communicate()
            cidr = str(output3.decode('utf-8').strip())
        except Exception as e:
            logging.error(e)

        logging.info('Returned the cidr %s'%cidr)

        gateway = '0.0.0.0'
        try:
            proc2 = subprocess.Popen("sudo ip route | awk '/default/ { print $3 }'", stdout=subprocess.PIPE, shell=True)
            (output2, err2) = proc2.communicate()
            gateway = str(output2.decode('utf-8').strip())
        except Exception as e:
            logging.error(e)

        logging.info('Returned the gateway %s'%gateway)
        
        dnsarray = []
        try:
            dns = subprocess.Popen("sudo nmcli device show '%s' | grep IP4.DNS"%nic, stdout=subprocess.PIPE, shell=True)
            (dnsoutput, dnserr) = dns.communicate()
            dns_out = dnsoutput.decode('utf-8').strip().split('\n')
        except Exception as e:
            logging.error(e)

        if len(dns_out) > 0:
            for dns in dns_out:
                d = dns.split()
                dnsarray.append(d[1])

        logging.info('Returned the DNS servers %s'%dnsarray)

        return {'ip':ip, 'gateway':gateway,'cidr':cidr,'dns':dnsarray}

    def set_nic_ip_info(self, input_dict):
        """
        DESC: Set new ip info on the device
        INPUT: input_dict - ip - req no
                          - cidr - req no
                          - gateway - req no
                          - dns - array of dns servers - req no
                          - dhcp - True or False - req yes
        OUTPUT: out_dict  - old_ip
                          - new_ip
                          - old_cidr
                          - new_cidr
                          - old_gateway
                          - new_gateway
                          - old_dns
                          - new_dns
                          - dhcp
        NOTES: in order to set the device to dhcp set the ip key
        """
        #set the flags
        dhcp_flag = ip_flag = dns_flag = False
        
        #pull the old ip info
        old_info = self.get_nic_ip_info()
        
        #ensure all of the keys are lower case
        input_dict = dict((k.lower(), v) for k, v in input_dict.items())

        #if nothing is submitted then just set the default to True
        if 'dhcp' not in input_dict and input_dict['dhcp'] is not True:
            input_dict['dhcp'] = True
        
        if input_dict['dhcp']:
            logging.info('Setting the device to DHCP.')
            #use nmcli to set ip
            try:
                newip = subprocess.Popen("sudo nmcli con modify %s ipv4.addresses ''"%(nic), stdout=subprocess.PIPE, shell=True)
                (ipoutput, iperr) = newip.communicate()
                ip_out = ipoutput.decode('utf-8').strip().split('\n')
                dhcp_flag = True
            except Exception as e:
                logging.error(e)
                logging.error('Could not set the ip on the device to dhcp.')

            try:
                #nmcli con mod enps03 ipv4.dns “8.8.8.8”
                nd = subprocess.Popen("sudo nmcli con modify %s ipv4.dns ''"%(nic), stdout=subprocess.PIPE, shell=True)
                (ndoutput, nderr) = nd.communicate()
                nd_out = ndoutput.decode('utf-8').strip().split('\n')
                dns_flag = True
            except Exception as e:
                logging.error(e)
                logging.error('Could not set DNS on the device to dhcp.')
            
        elif input_dict['dhcp'] is False:
            if 'ip' in input_dict and input_dict['ip'] != None:
                logging.info('Updateing the IP info.')
                #check the cidr
                if 'cidr' not in input_dict and input_dict['cidr'] == None:
                    input_dict['cidr'] = old_info['cidr']
                #use nmcli to set ip
                try:
                    newip = subprocess.Popen("sudo nmcli con modify %s ipv4.addresses %s/%s"%(nic,input_dict['ip'],input_dict['cidr']), stdout=subprocess.PIPE, shell=True)
                    (ipoutput, iperr) = newip.communicate()
                    ip_out = ipoutput.decode('utf-8').strip().split('\n')
                    ip_flag = True
                except Exception as e:
                    logging.error(e)
                    logging.error('Could not set the ip on the device.')
            
            if 'dns' in input_dict and input_dict['dns'] != None and len(input_dict['dns']):
                logging.info('Updateing the DNS settings.')
                #combine the old and new dns lists
                if len(old_info['dns']) > 0: 
                    newdns = input_dict['dns'] + old_info['dns']
                    newdns = list(dict.fromkeys(newdns))
                else:
                    newdns = input_dict['dns']
                
                try:
                    #nmcli con mod enps03 ipv4.dns “8.8.8.8”
                    nd = subprocess.Popen("sudo nmcli con modify %s ipv4.dns %s"%(nic,",".join(newdns)), stdout=subprocess.PIPE, shell=True)
                    (ndoutput, nderr) = nd.communicate()
                    nd_out = ndoutput.decode('utf-8').strip().split('\n')
                    dns_flag = True
                except Exception as e:
                    logging.error(e)
                    logging.error('Updated the DNS settings.')
        
        else:
            logging.warn('Can not set ip info, please check the settings.')

        if (dns_flag and ip_flag) or dhcp_flag:
            return {'old_ip': old_info['ip'],
                    'new_ip': input_dict['ip'],
                    'old_cidr': old_info['cidr'],
                    'new_cidr': input_dict['cidr'],
                    'old_gateway': old_info['gateway'],
                    'new_gateway': input_dict['gateway'],
                    'old_dns': old_info['dns'],
                    'new_dns': newdns}

    def list_nics(self):
        """
        DESC: List the available nics
        INPUT: None
        OUTPUT: out_array - list of nics
        NOTES: None
        """
        out_array = []
        try:
            proc = subprocess.Popen("sudo ls -I br* -I lo -I vir* /sys/class/net/", stdout=subprocess.PIPE, shell=True)
            (output, err) = proc.communicate()
            out_array = output.decode('utf-8').strip().split()
        except Exception as e:
            logging.error(e)
            logging.error("Could not get the list of nics")

        logging.info(out_array)

        return out_array