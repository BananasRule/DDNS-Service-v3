## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.


from mainconfigprocessor import *
import commonexception as comex
import logging
import time
import os

# Create logger
logging.basicConfig(filename="ddnsagent.log", level=logging.INFO, force=True,
                    format="%(asctime)s: %(process)d-%(levelname)s - %(message)s")
logger = logging.getLogger()
logger.info("Script started.")
# Load data from last run
loc = os.getcwd()
try:
    last_run_data = open("../data/run.data")
    failure, last_ipv4_address, last_ipv6_address, error_email_time, last_run_time = (
        last_run_data.readline().strip().split(","))
except FileNotFoundError or ValueError:
    # Allow for an exception if data file is not found
    logger.warning("Data file not found. Assuming worst case (Failure occurred, no email sent).")
    failure = True
    last_ipv4_address = "0"
    last_ipv6_address = "0"
    error_email_time = "0"
    last_run_time = "0"
else:
    logger.info("Data loaded.")
    last_run_data.close()

# Process last run data and convert to usable variables
if failure == "0":
    failure = False
else:
    failure = True

if last_ipv4_address == "0":
    last_ipv4_address = None

if last_ipv6_address == "0":
    last_ipv6_address = None

# If time cannot be converted to int set to 0
try:
    last_run_time = int(last_run_time)
except ValueError:
    last_run_time = 0

try:
    error_email_time = int(error_email_time)
except ValueError:
    error_email_time = 0


# Load config
applet_block = mainconfigloader()

# Get current IP addresses
if applet_block.ipv4_service is not None:
    ipv4_address = applet_block.ipv4_service.get()
else:
    ipv4_address = None
if applet_block.ipv6_service is not None:
    ipv6_address = applet_block.ipv6_service.get()
else:
    ipv6_address = None

# Define conditions for an update
# Change in ip address, failure occurred in last run or over 1 hour since last check
if ipv4_address != last_ipv4_address or ipv6_address != last_ipv6_address or failure or \
        last_run_time > int(time.time()) + 3600:

    logger.info("Update / domain check required.")

    # Create email message
    email_message = ""

    # Create failure flag
    failure = False

    # Create update flag
    update = False

    # Check that an ip service is defined for all records
    for domain_record in applet_block.domain_records:
        if domain_record.IP_type == "A" and ipv4_address is None:
            comex.log_fatal(logger, "IPv4 record listed but no IPv4 service URL was listed.")
        elif domain_record.IP_type == "AAAA" and ipv6_address is None:
            comex.log_fatal(logger, "IPv6 record listed but no IPv6 service URL was listed.")

    # Get all records
    dns_records = applet_block.dns_api.get_all_records(applet_block.domain_records)

    # Iterate over domains updating records
    for domain_record_info in dns_records:

        if domain_record_info.domain.IP_type == "A":
            ip_address = ipv4_address
        elif domain_record_info.domain.IP_type == "AAAA":
            ip_address = ipv6_address
        else:
            ip_address = None   # Program will terminate
            comex.log_fatal(logger, "Domain with unrecognised IP_type in list.")

        # Update domain status if required
        update_status = applet_block.dns_api.multi_update(domain_record_info.records, domain_record_info.domain,
                                                          ip_address)

        # Create email message
        email_message = applet_block.mail_service.compose(update_status.success, update_status.failure,
                                                          domain_record_info.domain.zone_name, email_message)

        # Check if a failure occurred
        if len(update_status.failure) != 0:
            failure = True

        # Check if update occurred
        if len(update_status.success) != 0:
            update = True

    logger.info("DNS Records Updated.")

    # Determine ip address to send in email
    if ipv4_address is not None and ipv6_address is not None:
        ip_address = ipv4_address + ", " + ipv6_address
    elif ipv4_address is not None:
        ip_address = ipv4_address
    elif ipv6_address is not None:
        ip_address = ipv6_address
    else:
        ip_address = "UNDETERMINED"

    # Create email footer
    email_message = applet_block.mail_service.footer(email_message, ip_address)

    # Create email subject
    if not failure:
        subject = "DNS update succeeded"
    else:
        subject = "DNS update failed"

    # Check if email should be sent
    # Send if:
    # Error email not sent in last hour and a failure has occurred
    # Update occurred
    if (error_email_time > int(time.time()) + 3600 and failure) or update:
        applet_block.mail_service.send(subject, email_message)
        logger.info("Email Sent.")
        if failure:
            error_email_time = int(time.time())

    # Open data file for writing
    run_data = open("../data/run.data", "w")
    # Check for failure
    if not failure:
        fail_val = "0"
    else:
        fail_val = "1"

    # Set ip address to 0 if none
    if ipv4_address is None:
        ipv4_address = "0"
    if ipv6_address is None:
        ipv6_address = "0"

    # Write data
    run_data.write(fail_val + "," + ipv4_address + "," + ipv6_address + "," + str(error_email_time) + "," +
                   str(int(time.time())))
    run_data.close()

    # Log success and terminate
    logger.info("Run successful.")

else:
    logger.info("Update not required.")
