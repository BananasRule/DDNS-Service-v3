#!/bin/bash

cd /opt/DDNS-Service-v3
wget https://github.com/BananasRule/DDNS-Service-v3/releases/latest/download/update-package.zip
unzip -o update-package.zip
rm update-package.zip

cd /opt
chown -R ddnsagent:ddns DDNS-Service-v3
su ddnsagent -c "cd /opt && chmod 770 -R DDNS-Service-v3"
