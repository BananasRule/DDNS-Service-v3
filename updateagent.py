import subprocess
import time

print("Welcome to the DDNS Service v3 update agent.")
print("This software is licenced under MPL2.0, a copy of which can be found here: "
      "https://github.com/BananasRule/DDNS-Service-v3/blob/main/LICENSE.txt")
print("This license includes a disclaimer of warranty and limitation of liability.")
print("By agreeing you explicitly agree to the disclaimer of warranty and limitation of liability in addition agreeing "
      "to the full license.")
print("By agreeing you declare you have read, understood and have the capability to enter into and agree this license.")

time.sleep(3)

acceptance = input("Do you agree to these terms? [Y/N]")

if acceptance != "Y":
    print("Terms declined. Updater will now exit.")
else:
    print("Downloading updated manifest file.")
    subprocess.run("/opt/DDNS-Service-v3/scripts/updater/get_latest_manifest.sh")

latest_manifest = open("/opt/DDNS-Service-v3/data/latest.manifest")
current_manifest = open("/opt/DDNS-Service-v3/data/current.manifest")

latest_man_details = {}
current_man_details = {}

for line in latest_manifest:
    item, value = line.strip().split("=", 1)
    latest_man_details[item] = value

for line in current_manifest:
    item, value = line.strip().split("=", 1)
    current_man_details[item] = value

if int(latest_man_details["updaterversion"]) > int(current_man_details["updaterversion"]):
    supportver = latest_man_details["updatercompatibility"].split(",")
    if current_man_details["updaterversion"] in supportver:
        print("An update to the updater is required to proceed.")
        print("It can be automatically installed.")
        print("Update notes:")
        print(latest_man_details["updaternotes"])
        acceptance = input("Would you like to proceed? [Y/N]")

        if acceptance == "Y":
            subprocess.run("/opt/DDNS-Service-v3/scripts/updater/update_updater.sh")
            print("Please relaunch updater.")
        else:
            print("Program will now exit.")
    else:
        print("Update to the updater is required to proceed.")
        print("It cannot be automatically installed.")
        print("Program will now exit.")
else:
    print("Updater is up to date.")
    if int(latest_man_details["programversion"]) > int(current_man_details["programversion"]):
        supportver = latest_man_details["programcompatibility"].split(",")
        if current_man_details["programversion"] in supportver:
            print("An update is available.")
            print("It can be installed automatically.")
            print("Update notes:")
            print(latest_man_details["programnotes"])
            acceptance = input("Would you like to proceed? [Y/N]")
            if acceptance == "Y":
                subprocess.run("/opt/DDNS-Service-v3/scripts/updater/update_main.sh")
                print("Updated main.")
            else:
                print("Program will now exit.")
        else:
            print("An update is available")
            print("It cannot be automatically installed.")
            print("Program will now exit.")





