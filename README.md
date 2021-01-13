# Speedbot

The speedbot appliance will check your internet upload and download speed on a periodic basis. MQTT can be activated on the speedbot to send data back to an MQTT server to store and analyze metrics.

---

# Part 1 - Overview
## Hardware components needed
If you are a hobbiest you may have all of the parts needed to build out the Speedbot device. 
* [Iconikal Rockchip RK3328] - The Speedbot computer
* [16x2 Serial LCD display I2C] - 16 column LCD display.
* [5V 3A Power adapter] - 5V power adapter

[Iconikal Rockchip RK3328]: <https://liliputing.com/2020/09/this-10-single-board-computer-is-faster-than-a-raspberry-pi-3.html>
[16x2 Serial LCD]: <https://circuitdigest.com/article/16x2-lcd-display-module-pinout-datasheet/>
[Package]: <https://www.amazon.com/gp/product/B0868WSTXH/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1>

## Software libraries needed
All of the codeing for PiTemp is done using Python3. The reason I chose Python to build PiTemp is because it is easy to understand and can be picked up easily. It isalso one of the mpost popular programming langauges around, and can be used to build everything from simple scripts to machine learning alrorythems.

* [OS] - Raspberry Pi OS/Raspbian 9
* [Python3] - The base language used in PiTemp.
* [AdafruitDHT] - An open source DHT11 control library.
* [AdafruitSSD1306] - An open source OLED control library.
* [PahoMqtt] - The Pyhton MQTT library used to send data.
* [Sqlite3] - A simple database used to store metrics.
* [Schedule] - The Python time scheduling library.
* [PIL] - Python imaging library.
* [RpiGPIO] - Python class to control Rpi GPIO interface.
* [jinja2] - Expressive template libraryBlinka.
* [Blinka] - Adafruit Blinka provides a programming interface for Rpi microcontroller.
* [PlatformDetect] - Adafruit best guess platform detection library
* [Pureio] - Pure Python access to SPI and I2C

[Python3]: <https://www.python.org/>
[AdafruitDHT]: <https://github.com/adafruit/Adafruit_Python_DHT>
[AdafruitSSD1306]: <https://github.com/adafruit/Adafruit_SSD1306>
[PahoMqtt]: <https://www.eclipse.org/paho/>
[Sqlite3]: <https://docs.python.org/3/library/sqlite3.html>
[Schedule]: <https://pypi.org/project/schedule/>
[PIL]: <https://www.pythonware.com/products/pil/>
[RpiGPIO]: <https://pypi.org/project/RPi.GPIO/>
[jinja2]: <https://pypi.org/project/Jinja2/>
[Blinka]: <https://pypi.org/project/Adafruit-Blinka/>
[PlatformDetect]: <https://pypi.org/project/Adafruit-PlatformDetect/>
[Pureio]: <https://github.com/adafruit/Adafruit_Python_PureIO/tree/1.0.4>
[OS]: <https://www.raspberrypi.org/downloads/>

## Python library versions
|  Library | Version  |
| ------------ | ------------ |
|  rpi.gpio |  0.7.0 |
|  jinja2 | 2.10.1  |
|  adafruit-blinka |  4.2.0 |
|  schedule | 0.6.0  |
| adafruit-ssd1306  | 1.6.2  |
| adafruit-dht | 1.4.0 |
| adafruit-platformdetect | 2.5.0 |
| adafruit-pureio | 1.0.4 |
| paho-mqtt | 1.5.0 |
| gunicorn | 20.0.4 |
| requests | 2.21.0 |
| multiprocess | 0.70.10 |

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
