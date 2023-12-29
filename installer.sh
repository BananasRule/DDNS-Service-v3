#!/bin/bash

## © Jacob Gray 2022
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.

#Check that script is running as root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


#License agreement
#Make user aware under which license they are installing the software and get their agreement
echo "Preparing to install DDNS-Service"
echo "Please agree to the license terms to continue: "
echo "This software is licenced under MPL2.0, a copy of which can be found here: https://github.com/BananasRule/DDNS-Service-v3/blob/main/LICENSE.txt"
echo "This license includes a disclaimer of warranty and limitation of liability."
echo "By agreeing you explicitly agree to the disclaimer of warranty and limitation of liability in addition agreeing to the full license."
echo "By agreeing you declare you have read, understood and have the capability to enter into and agree this license."
#Force user to read above paragraph
sleep 5
#Check acceptance with agreement
read -p "Do you agree to the license terms? (Y/N): " acceptance
acceptance=${acceptance^^}
if [ "${acceptance}" = "Y" ]
then
#Install dependencies
echo "Thank you for agreeing to the license terms. Installation will now begin."
apt update
apt upgrade -y
apt install unzip -y
apt install python3 -y
apt install python3-pip -y
pip install requests

#Create folder
cd /opt
mkdir DDNS-Service-v3
cd DDNS-Service-v3
#Download software from latest release and unzip
wget https://github.com/BananasRule/DDNS-Service-v3/releases/latest/download/DDNS-Service-v3-Release.zip
unzip DDNS-Service-v3-Release.zip
rm DDNS-Service-v3-Release.zip

#Copy example config and open config file for user to enter data to
cd config
cp example_config.conf config.conf
nano config.conf


#Create group
addgroup ddns

#Create user account for agent
usrpasswd="$(pwgen -s $((${RANDOM:0:2} + 30 )))"
adduser --disabled-password --gecos "" ddnsagent
usermod -aG ddns ddnsagent
echo -e "$usrpasswd\n$usrpasswd\n" | passwd ddnsagent

echo "User: ddnsagent, Group: ddns, Password: $usrpasswd"

#Assign folder ownership
cd /opt
chown -R ddnsagent:ddns DDNS-Servicev2

#Protect folder from unauthorised access
su ddnsagent -c "cd /opt && chmod 770 -R DDNS-Servicev2"

#Add cronjob to run every minute
su ddnsagent -c "cd && crontab -l > tempcron"
su ddnsagent -c "cd && echo \"* * * * * cd /opt/DDNS-Service-v3 && python3 /opt/DDNS-Service-v3/DDNSUpdateService.py\" >> tempcron"
su ddnsagent -c "cd && crontab tempcron"
su ddnsagent -c "cd && rm tempcron"
service cron restart

echo "Installation complete"

fi