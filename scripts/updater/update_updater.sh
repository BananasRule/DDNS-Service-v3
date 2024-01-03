#!/bin/bash

## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Download update package and overwrite existing applications
cd /opt/DDNS-Service-v3
wget https://github.com/BananasRule/DDNS-Service-v3/releases/latest/download/update-package.zip
unzip -o update-package.zip
rm update-package.zip

# Take ownership of new files for ddnsagent user / ddns group and apply permissions
cd /opt
chown -R ddnsagent:ddns DDNS-Service-v3
su ddnsagent -c "cd /opt && chmod 770 -R DDNS-Service-v3"
