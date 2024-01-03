## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.


import subprocess
import time
import os

# Check that update agent is running as root
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\n"
         "Please try again using sudo python3 updateagent.py. Exiting.")

# Print welcome and license
print("Welcome to the DDNS Service v3 update agent.")
print("This software is licenced under MPL2.0, a copy of which can be found here: "
      "https://github.com/BananasRule/DDNS-Service-v3/blob/main/LICENSE.txt")
print("This license includes a disclaimer of warranty and limitation of liability.")
print("By agreeing you explicitly agree to the disclaimer of warranty and limitation of liability contained within the "
      "MPL 2.0 license.")
print("By agreeing you declare you have read, understood and have the capability to enter into and agree this license.")

# Delay to allow reading of license
time.sleep(3)

# Check user agreement to license conditions
acceptance = input("Do you agree to these terms? [Y/N]: ")

if acceptance != "Y":
    print("Terms declined. Updater will now exit.")
else:
    # Download latest manifast files
    print("Downloading updated manifest file.")
    subprocess.run("/opt/DDNS-Service-v3/scripts/updater/get_latest_manifest.sh")
    latest_manifest = open("/opt/DDNS-Service-v3/data/latest.manifest")
    current_manifest = open("/opt/DDNS-Service-v3/data/current.manifest")

    # Load manifest details
    latest_man_details = {}
    current_man_details = {}

    for line in latest_manifest:
        if len(line.strip()) > 0:
            item, value = line.strip().split("=", 1)
            latest_man_details[item] = value

    for line in current_manifest:
        if len(line.strip()) > 0:
            item, value = line.strip().split("=", 1)
            current_man_details[item] = value

    # Close manifest file and clean up file
    current_manifest.close()
    latest_manifest.close()
    os.remove("/opt/DDNS-Service-v3/data/latest.manifest")

    # Check if an update is required
    if int(latest_man_details["updaterversion"]) > int(current_man_details["updaterversion"]):

        # Check if the update is listed as supported
        supportver = latest_man_details["updatercompatibility"].split(",")
        if current_man_details["updaterversion"] in supportver:
            # Ask for user consent to update
            print("An update to the updater is required to proceed.")
            print("It can be automatically installed.")
            print("Update notes:")
            print(latest_man_details["updaternotes"])
            acceptance = input("Would you like to proceed? [Y/N]: ")

            if acceptance == "Y":
                # Run the download script and patch the current manifest
                subprocess.run("/opt/DDNS-Service-v3/scripts/updater/update_updater.sh")
                current_manifest = open("/opt/DDNS-Service-v3/data/current.manifest", "a")
                current_manifest.write("\nupdaterversion="+latest_man_details["updaterversion"])
                print("Please relaunch updater.")
            else:
                print("Program will now exit.")
        else:
            # If the update is not supported advise a manual install
            print("Update to the updater is required to proceed.")
            print("It cannot be automatically installed.")
            print("Program will now exit.")
    else:
        print("Updater is up to date.")
        # Check if there is an update to the main program
        if int(latest_man_details["programversion"]) > int(current_man_details["programversion"]):
            supportver = latest_man_details["programcompatibility"].split(",")
            if current_man_details["programversion"] in supportver:
                # Ask for user consent to update
                print("An update is available.")
                print("It can be installed automatically.")
                print("Update notes:")
                print(latest_man_details["programnotes"])
                acceptance = input("Would you like to proceed? [Y/N]: ")

                if acceptance == "Y":
                    # Run updater script
                    subprocess.run("/opt/DDNS-Service-v3/scripts/updater/update_main.sh")
                    print("Program successfully updated.")
                else:
                    print("Program will now exit.")
            else:
                # If the update is not supported advise a manual install
                print("An update is available")
                print("It cannot be automatically installed.")
                print("Program will now exit.")
        else:
            print("DDNS Agent is up to date. Exiting.")




