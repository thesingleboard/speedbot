#!/bin/bash -x

sudo apt-get update
sudo apt-get upgrade

apt install docker.io
systemctl enable docker
systemctl start docker

apt-get install network-manager
systemctl start NetworkManager.service
systemctl enable NetworkManager.service

#Generate an unchangable nodeID
NODEONE=$(($RANDOM % 99999999 + 10000000))
NODETWO=$(($RANDOM % 99999 + 10000))
HOSTNAME=ciac-${NODETWO}
NODEID=000-${NODEONE}-${NODETWO}
echo $NODEID > /etc/nodeid
chown speedbot:speedbot /etc/nodeid
chmod 0444 /etc/nodeid

hostnamectl set-hostname $NODEID

#Create datastores
mkdir -p /home/speedbot
mkdir -p /opt/speedbot-data

#speedbot user
useradd -U -d /home/speedbot -s /bin/bash speedbot
chown speedbot:speedbot /home/speedbot
echo -e 'speedbot\nspeedbot\n' | passwd speedbot

#add speedbot to the docker group
usermod -aG docker speedbot

#set up rbash
ln -s /bin/bash /bin/rbash
echo '/bin/rbash' >> /etc/shells
echo '/bin/admin.sh' >> /etc/shells

#copy botcli
cp device/botcli.py /opt/botcli.py

#Custom shell for config
touch /bin/admin.sh
(
cat <<'EOP'
#!/bin/rbash
python /opt/botcli.py
EOP
) >> /bin/admin.sh

chmod +x /bin/admin.sh
chown speedbot:speedbot /bin/admin.sh

#create an admin for the shell config
useradd -d /home/admin -g speedbot -s /bin/admin.sh admin

#set admin default password
echo -e 'password\npassword\n' | passwd admin

# start and stop the container
cp -f systemd/start-speedbot /bin
cp -f systemd/stop-speedbot /bin
cp -f systemd/restart-speedbot /bin
cp -f systemd/fresh-start-speedbot /bin
cp -f systemd/factory-reset-speedbot /bin

chmod 755 /bin/start-speedbot
chmod 755 /bin/stop-speedbot
chmod 755 /bin/restart-speedbot
chmod 755 /bin/fresh-start-speedbot
chmod 755 /bin/factory-reset-speedbot

cp etc/speedbot.cfg /etc/speedbot.cfg

source /etc/speedbot.cfg

#cp -f systemd/speedbot.service /etc/systemd/system/

#chmod 664 /etc/systemd/system/speedbot.service

#systemctl daemon-reload

#docker pull the latest speedbot
docker pull speedbot:stable
#docker tag the latest speedbot for factory reset
docker tag speedbot:stable factory/speedbot:factory

#fire up the speedbot container as a daemon
docker run -d -h speedbot --network=host --privileged -p 10500:10500 -v /opt/speedbot-data:/opt/speedbot-data --name speedbot -e PINS=$PINS -e INTERVAL=$INTERVAL -e MQTTBROKER=$MQTTBROKER -e MQTTPORT=$MQTTPORT -e API=$API speedbot:$VERSION

#systemctl enable speedbot.service

#Set speedbot container to fire up on system boot/reboot
#sed -i 's/exit\ 0/source\ \/etc\/speedbot.cfg\ndocker\ start\ speedbot\nexit\ 0/g' /etc/rc.local
#NOTE: Also changed rc.local to use bash
sed -i 's/exit\ 0/\/bin\/start-speedbot\nexit\ 0/g' /etc/rc.local
