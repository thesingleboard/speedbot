sudo docker run -d -h speedbot --network=host --privileged -v /opt/speedbot-data:/opt/speedbot-data --name speedbot -e PINS="28,27" -e INTERVAL=3600 -e MQTTBROKER='192.168.1.61' -e MQTTPORT='8883' -e API='1.0' speedbot:latest

#sudo docker run -ti -h speedbot --network=host --privileged -p 10400:10400 -v /opt/speedbot-data:/opt/speedbot-data --name speedbot \
#-e PINS="28,27" \
#-e INTERVAL=10 \
#-e MQTTBROKER='192.168.1.61' \
#-e MQTTPORT='8883' \
#-e API='1.0' \
#speedbot:latest bash

#-e SENSORTYP='DHT11' \
#-e SCALE='Fahrenheit' \
#-e PINS="24,23,4" \
#-e SLEEP=2 \
#-e RST='None' \
#-e INTERVAL=1 \
#-e PHYSNET='wlan0' \
#-e MQTTBROKER='192.168.1.61' \
#-e MQTTPORT='8883' \
#-e SSLCERTPATH='/opt/pitemp/certs' \
#-e SSLCERT='ca.crt' \
#pitemp
#--privileged