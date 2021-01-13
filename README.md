# Speedbot

The speedbot appliance will check your internet upload and download speed on a periodic basis. MQTT can be activated on the speedbot to send data back to an MQTT server to store and analyze metrics.

# Part 1 - Overview
## Hardware components needed
## Software libraries needed
## Python library versions
## Architectural diagram
### Bread Board
### Schematic
# Part 2 - Build the Speedbot
## Set up the Speedbot
## Build a simple MQTT broker
In order to develop and test the PiTemp and the MQTT protocol, you will need to deploy a simple broker to recive the data sent by the PiTemp. The MQTT protocol uses SSL to protect data, and as a best practice should be used in IoT communication channels. The MQTT protocol is used in IoT applications because of it speed and the fault tolerant nature of the protocol.

MQTT - https://mqtt.org/

```
#!/bin/bash

sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service

#configure the ca certs
#NOTE: This is on raspbian
#generate the certificate authority key
sudo openssl genrsa -aes128 -out ca.key -passout pass:mynewpassword 3072

#create a certificate
sudo openssl req -new -passin pass:mynewpassword -x509 -days 2000 -key ca.key -out ca.crt -subj "/C=US/ST=Home/L=HOME/O=Global Security/OU=MQTT Department/CN=nothing.com"

#generate server keys pairs for the broker
sudo openssl genrsa -out server.key 2048

#create the server csr
sudo openssl req -new -out server.csr -key server.key -subj "/C=US/ST=Home/L=HOME/O=Global Security/OU=MQTT Department/CN=nothing.com"

#create the server cert signed with the ca key
sudo openssl x509 -passin pass:mynewpassword -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360

#Copy the certs to the proper location on the broker
sudo cp ca.crt /etc/mosquitto/ca_certificates/
sudo cp server.crt /etc/mosquitto/ca_certificates/
sudo cp server.key /etc/mosquitto/ca_certificates/

#copy the client certs to a client folder
sudo mkdir client_cert
sudo cp ca.crt ./client_cert

#Configure the broker
sudo mv /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.old

#build a Mosquitto config file
sudo cat /etc/mosquitto/mosquitto.conf <<EOF
pid_file /var/run/mosquitto.pid

persistence true
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

include_dir /etc/mosquitto/conf.d

#port 8883 is the MQTT secure port
listener 8883
cafile /etc/mosquitto/ca_certificates/ca.crt
keyfile /etc/mosquitto/ca_certificates/server.key
certfile /etc/mosquitto/ca_certificates/server.crt

EOF

#Start Mosquitto broker
sudo mosquitto -d -v -c /etc/mosquitto/mosquitto.conf
```
## Create new certificates
If you need to build a new set of certificates for SSL, use the following script.

```
#!/bin/bash -x
#generate the certificate authority key
openssl genrsa -aes128 -out ca.key -passout pass:mynewpassword 3072

#create a certificate
openssl req -new -passin pass:mynewpassword -x509 -days 2000 -key ca.key -out ca.crt -subj "/C=US/ST=Home/L=HOME/O=Global
Security/OU=MQTT Department/CN=nothing.com"

#generate server keys pairs for the broker
openssl genrsa -out server.key 2048

#create the server csr
openssl req -new -out server.csr -key server.key -subj "/C=US/ST=Home/L=HOME/O=Global Security/OU=MQTT Department/CN=nothi
ng.com"

#create the server cert signed with the ca key
openssl x509 -passin pass:mynewpassword -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days
 360
```
# Part 3 - How it works
## Hardware Components
# Part 4 - Extra Credit
