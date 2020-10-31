FROM python:3.8.2-slim-buster
MAINTAINER Jonathan Arrance <jonathan@thesingleboard.io>

ENV INSTALL_PATH /opt/speedbot
#ENV CERT_PATH /opt/pitemp/certs

RUN apt-get update -y;apt-get install -y curl;apt-get install -y python3-pip;apt install -y python3-dev;apt install -y python-imaging; apt install -y python-smbus;apt install -y i2c-tools; \
apt install -y python3-pil;apt install -y python3-setuptools;apt install -y python-smbus;apt-get install -y libgpiod2;apt install -y i2c-tools;apt install -y python3-openssl

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

RUN pip3 install --upgrade pip
ADD requirements.txt /
RUN pip3 install -r /requirements.txt

ADD speedbot.py $INSTALL_PATH
ADD speedbot_lib.py $INSTALL_PATH
ADD run_app.py $INSTALL_PATH
ADD entrypoint.sh $INSTALLPATH
ADD settings.py $INSTALL_PATH
#ADD ca.crt $CERT_PATH

#MQTT - secure
#EXPOSE 8883

#API - secure
EXPOSE 10500

#CMD ["python","pitemp.py"]

ENTRYPOINT["python3","run-app.py"]
