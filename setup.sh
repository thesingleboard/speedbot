VERSION='nightly-v25'
MASTER_PWD="simpleprivatecloudsolutions"

chkconfig ntpd on
service ntpd restart

#create a speedbot dir
mkdir -p /usr/local/lib/python3.6/speedbot/

#set the hostname to sb-xxxxx random digits
echo "Setting the hostname."
mv /etc/hostname /etc/hostname.old
#RAND=$RANDOM

NODEONE=$(($RANDOM % 99999999 + 10000000))
NODETWO=$(($RANDOM % 99999 + 10000))

HOSTNAME=sb-${NODETWO}

#ciac node id
NODEID=000-${NODEONE}-${NODETWO}

echo $NODEID > /etc/nodeid

#set up rbash
ln -s /bin/bash /bin/rbash
echo '/bin/rbash' >> /etc/shells
echo '/bin/admin.sh' >> /etc/shells

#create admin shell - admin.sh
touch /bin/admin.sh
(
cat <<'EOP'
#!/bin/rbash
python2.7 /usr/local/lib/python3.6/speedbot/interfaces/shell/action.py
EOP
) >> /bin/admin.sh
chmod +x /bin/admin.sh
chown transuser:transystem /bin/admin.sh

#add the admin user
useradd -d /home/admin -g transystem -s /bin/admin.sh admin

#set admin default password
echo -e 'password\npassword\n' | passwd admin

#make it so apaceh can run sudo
sed -i 's/Defaults    requiretty/#Defaults    requiretty/g' /etc/sudoers

#echo "Setting up transuser sudo."
#set the transuser account up in sudo
(
cat <<'EOP'
admin ALL=(ALL) NOPASSWD: ALL
apache ALL=(ALL:ALL) NOPASSWD: ALL
EOP
) >> /etc/sudoers

#fix postgres user groups
usermod -a -G postgres admin
usermod -a -G postgres apache
usermod -a -G postgres transuser
