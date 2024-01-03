# DDNS-Service-v3
A DDNS agent service designed to update DNS records to reflect changes to the servers IP address. 

**Any and all use, and/or other interaction with this application and/or codebase is subject to the terms of the MPL 2.0 
license found the LICENSE.txt document. 
This license includes an explicit Limitation of Liability and Disclaimer of Warranty.**



THIS APPLICATION IS NOT ENDORSED, SPONSORED OR ASSOCIATED WITH Cloudflare®

THIS APPLICATION USES THE Cloudflare® API V4

# About
This is a python application / script designed to update DNS records to reflect changes to a servers IP address.
Currently, only Cloudflare® is supported by this application but it is designed to allow for the inclusion of other
DNS services in the future. 

# Operation
This program is designed to check for IP address changes every minute, with a check of the DNS record occurring hourly. 
It is able to email the status of DNS updates to a designated email address using SMTP. 

# Install
An installation script is provided and can be run using the following command:

``` wget https://github.com/BananasRule/DDNS-Service-v3/releases/latest/download/installer.sh && sudo bash installer.sh ```

This script must be run as root. It will create a user account and user group for use with the agent. 

# Update
You are able to update the software using the update agent: ```sudo python3 /opt/DDNS-Service-v3/updateagent.py```. 
This must be run as root. It will call scripts located in the scripts/updater folder. 

# Configuration File
The configuration file is located in ```/opt/DDNS-Service-v3/config/config.conf```

# Improvements over previous version 
Version 3 improves on version 2 in a number of ways that make it incompatible.

These include:
- Improvements to the update system
- Rewrite of the configuration loaders
- Better support for future expansion 
- Improved code documentation 

# Application Test
Tests are not functional and require further development.
