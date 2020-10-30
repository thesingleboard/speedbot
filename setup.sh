#set up rbash
ln -s /bin/bash /bin/rbash
echo '/bin/rbash' >> /etc/shells
echo '/bin/admin.sh' >> /etc/shells

#create admin shell - admin.sh
touch /bin/admin.sh
(
cat <<'EOP'
#!/bin/rbash
python2.7 /usr/local/lib/python2.7/transcirrus/interfaces/shell/coalesce.py
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
transuser ALL=(ALL) NOPASSWD: ALL
admin ALL=(ALL) NOPASSWD: ALL
apache ALL=(ALL:ALL) NOPASSWD: ALL
EOP
) >> /etc/sudoers

#fix postgres user groups
usermod -a -G postgres admin
usermod -a -G postgres apache
usermod -a -G postgres transuser
