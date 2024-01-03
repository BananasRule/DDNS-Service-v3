#!/bin/bash

## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Navigate to directory and download the latest manifest from github
cd /opt/DDNS-Service-v3/data
wget https://github.com/BananasRule/DDNS-Service-v3/releases/latest/download/latest.manifest

