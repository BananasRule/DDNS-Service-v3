#!/bin/bash

cd /opt/DDNS-Service-v3
rm -r data
wget https://github.com/BananasRule/DDNS-Service-v3/releases/latest/download/DDNS-Service-v3-Release.zip
unzip -o DDNS-Service-v3-Release.zip
rm DDNS-Service-v3-Release.zip

cd /opt
chown -R ddnsagent:ddns DDNS-Service-v3
su ddnsagent -c "cd /opt && chmod 770 -R DDNS-Service-v3"

