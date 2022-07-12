export PINS="28,27"
export INTERVAL=60
export MQTTBROKER='192.168.1.61'
export MQTTPORT='8883'
export PHYSNET='eth0'
export TEMP_SCALE='F'
export prometheus_multiproc_dir='/tmp/prom'
export PROM_MULTIPROC_DIR=${prometheus_multiproc_dir}
export API='0.1Alpha'
export LCD_ADDR=0x27
export LCD_OFF=5
export LCD_TYPE=2004
export PROM_PORT='9002'
export DB_PATH='/opt/speedbot-data/'
export VERSION='release'

export DOCKER_REPO='192.168.1.32:5000'
#port 8883 is the tls/ssl port. 1883 is no secure
#export SSLCERTPATH='/home/pi/Documents/pitemp/certs'
#export SSLCERT='ca.crt'