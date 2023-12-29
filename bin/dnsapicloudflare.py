from dnsapiinterface import DNSAPIInterface, DomainInfo, RecordInfo, UpdateInfo, DomainRecords
import commonexception as comex
import logging
import requests


# noinspection PyMissingConstructor
## Class to store domain level details
class CloudflareDomainInfo(DomainInfo):
    def __init__(self):
        self.filter = []
        self.filter_type = None
        self.zone_name = None
        self.zone_id = None
        self.zone_key = None
        self.IP_type = None


# noinspection PyMissingConstructor
## Class to store record details
class CloudflareRecordInfo(RecordInfo):
    def __init__(self, record_name: str, IP_address: str, record_id: str):
        self.record_name = record_name
        self.IP_address = IP_address
        self.record_id = record_id


# noinspection PyMissingConstructor
# Suppress naming for clarity - DNSAPICloudflare
# noinspection PyUnusedLocal
## Main class implementing _DNSAPI_Interface() interface
class DNSAPICloudflare(DNSAPIInterface):
    ## Create a DNSAPI Cloudflare variation object
    # @param apiinfo List [apitoken]
    def __init__(self, discard: [any]):
        self.logger = logging.getLogger(__name__)

    ## Function to return all records found using domaininfo
    # @param domain_info Object of CloudflareDomainInfo type
    # @returns record_info List of objects of CloudflareRecordInfo type
    # @throws FatalError Unable to access API, program should terminate
    def get_records(self, domain_info: CloudflareDomainInfo):
        # Create parameter for request
        request_params = {"type": domain_info.IP_type}

        # Create Auth headers
        request_headers = {
            "Authorization": ("Bearer " + domain_info.zone_key),
            "Content-Type": "application/json"
        }

        # Create URL
        url = "https://api.cloudflare.com/client/v4/zones/" + domain_info.zone_id + "/dns_records"

        # Attempt to execute request
        try:
            response = requests.get(url, headers=request_headers, params=request_params)
            response.raise_for_status()
        except requests.ConnectionError or requests.Timeout:
            # Except failure to connect
            comex.log_fatal(self.logger, "Unable to connect to Cloudflare API during GET. " +
                            "Program will now terminate.")
        except requests.HTTPError:
            # Except a non-200 status code
            comex.log_fatal(self.logger, "Received invalid response from Cloudflare API during GET. " +
                            "Program will now terminate.")
        else:
            # If request succeeds process into list of record objects
            records = response.json()["result"]
            record_info = []
            for record in records:
                domain_id = record["id"]
                domain_name = record["name"]
                ip_address = record["content"]
                record_info.append(CloudflareRecordInfo(domain_name, ip_address, domain_id))
            # Return list
            return record_info

    ## Function to operate with a list of all records
    # @param domainsinfo List of CloudflareDomainInfo objects
    # @returns List of object of DomainRecord type
    def get_all_records(self, domainsinfo: [CloudflareDomainInfo]) -> [DomainRecords]:
        # Run on each domain and create a formatted list
        all_records = []
        for domain_info in domainsinfo:
            records = self.get_records(domain_info)
            complete_record = DomainRecords(domain_info, records)
            all_records.append(complete_record)
        return all_records

    ## Function to patch records with new IP address
    # @param domain_info DomainInfo class object
    # @param record_info RecordInfo class object
    # @param current_IP Current IP address as a string
    def update(self, record_info: CloudflareRecordInfo, current_IP: str, domain_info: CloudflareDomainInfo) -> None:
        # Create data for update
        data = {
            "content": current_IP,
            "name": record_info.record_name,
            "type": domain_info.IP_type
        }

        # Create Auth Headers
        request_headers = {
            "Authorization": ("Bearer " + domain_info.zone_key),
            "Content-Type": "application/json"
        }

        # Create URL
        url = ("https://api.cloudflare.com/client/v4/zones/" + domain_info.zone_id + "/dns_records/" +
               record_info.record_id)

        # Attempt to issue patch request
        try:
            response = requests.patch(url, headers=request_headers, json=data)
            response.raise_for_status()
        except requests.ConnectionError or requests.Timeout:
            # Except failure to connect
            self.logger.warning("Unable to connect to Cloudflare API during PATCH.")
            raise UpdateError
        except requests.HTTPError:
            # Except a non-200 status code
            self.logger.warning("Received invalid response from Cloudflare API during PATCH.")
            raise UpdateError
        else:
            # Patch successful
            return

    ## Function to preform multiple updates on the same domain
    # @param domaininfo DomainInfo class object
    # @param recordsinfo An list of RecordInfo class object
    # @param currentIP Current IP address as a string
    # @returns UpdateInfo object with statuses
    def multi_update(self, records_info: [CloudflareRecordInfo], domain_info: CloudflareDomainInfo, current_ip: str) \
            -> UpdateInfo:
        logger = logging.getLogger(__name__)
        update_info = UpdateInfo()
        # Iterate through records_info
        for record_info in records_info:
            if record_info.record_name.split(".", 1)[0] in domain_info.filter:
                if domain_info.filter_type == 1 or domain_info.filter_type == -1:
                    if record_info.IP_address != current_ip:
                        try:
                            self.update(record_info, current_ip, domain_info)
                        except UpdateError:
                            update_info.failure.append(record_info.record_name)
                        else:
                            update_info.success.append(record_info.record_name)
                else:
                    logger.info("Record (" + record_info.record_name.split(".", 1)[0] + ") filtered.")
            else:
                if domain_info.filter_type == 0 or domain_info.filter_type == -1:
                    if record_info.IP_address != current_ip:
                        try:
                            self.update(record_info, current_ip, domain_info)
                        except UpdateError:
                            update_info.failure.append(record_info.record_name)
                        else:
                            update_info.success.append(record_info.record_name)
                else:
                    logger.info("Record (" + record_info.record_name.split(".", 1)[0] + ") filtered.")
        return update_info


## Class for an update error
class UpdateError(Exception):
    pass


## Function for creating the class and associated variables from a config file
# @param config An list of string containing the config for the DNS section
# @param variables An dictionary of stored variables
# @returns A DNSAPICloudflare Object and a list of CloudflareDomainInfo objects
def cloudflarednsconfigloader(config: [str], variables: {str: str}) -> [DNSAPICloudflare, [CloudflareDomainInfo]]:
    logger = logging.getLogger(__name__)
    dns_records = []
    dns_record = None
    for line in config:
        # If line indicates beginning of a zone
        if line == "!ZONE":
            # Check that a DNS zone is not already in progress
            if dns_record is not None:
                raise comex.log_fatal(logger, "Error in DNS Configuration. Overlapping Zones."
                                              " The program will now terminate.")
            else:
                # Create a blank DNS record
                dns_record = CloudflareDomainInfo()
        # If line indicates end of a zone
        elif line == "!!ZONE":
            # Check that a DNS record is in progress
            if dns_record is None:
                raise comex.log_fatal(logger, "Error in DNS Configuration. Zone closed before opened."
                                              " The program will now terminate.")
            else:
                # Check validity of DNS record, replacing with defaults or raising an error

                # Zone ID - Mandatory, No Default Possible
                if dns_record.zone_id is None:
                    raise comex.log_fatal(logger, "DNS Zone did not define zoneid. The program will now terminate")

                # Zone Key - Mandatory, No Default Possible
                if dns_record.zone_key is None:
                    raise comex.log_fatal(logger, "DNS Zone did not define zonekey. The program will now terminate")

                # IP Type - Mandatory, Default of "A"
                if dns_record.IP_type is None:
                    logger.warning("IP type not defined for zone. Assuming default of 'A'")
                    dns_record.IP_type = "A"

                # Zone Name - Mandatory, Default of iterative number
                if dns_record.zone_name is None:
                    logger.warning("DNS zone name is no defined. Assigning generic name.")
                    dns_record.zone_name = len(dns_records)

                # DNS Filter Type - Optional, Default of Off
                # DNS Filter - Optional, Default to None
                # Check to ensure an error in configuration is not present
                if dns_record.filter_type is None:
                    if dns_record.filter is not None:
                        logger.error("Domains specified for filtering but the filter type is not specified. "
                                     "Filter is disabled.")
                    dns_record.filter = []
                    dns_record.filter_type = -1
                elif dns_record.filter is None and dns_record.filter_type != -1:
                    logger.error("No domains specified in filter but a allow or deny filter was specified.")
                    dns_record.filter = []

                # Add complete record to list and then set current DNS record to Null
                dns_records.append(dns_record)
                dns_record = None
        else:
            # Split into setting and value
            setting, value = line.split("=", 1)
            # Check if the value is a variable, and replace it with the var
            if value[0] == "$":
                if value[1:] in variables:
                    value = variables[value]
                else:
                    comex.log_fatal(logger, "Variable used without assignment. Program will now terminate.")
            # Check that setting is not expected outside a zone
            if setting != "provider":
                # Check that setting is not outside a zone
                if dns_record is None:
                    comex.log_fatal(logger,
                                    "DNS Zone settings provided outside of DNS Zone. Program will now terminate.")
                else:
                    # Match setting and update the dns record with the value
                    match setting:
                        case "zone_name":
                            dns_record.zone_name = value
                        case "zone_id":
                            dns_record.zone_id = value
                        case "zone_api_key":
                            dns_record.zone_key = value
                        case "zone_filterlist":
                            dns_record.filter = []
                            for rule in value.split(","):
                                dns_record.filter.append(rule.strip())
                        case "zone_filter":
                            # Test to see if word is in allow / deny list - Default to off
                            if value.lower() in ["allow", "only", "include"]:  # Allow
                                dns_record.filter_type = 1
                            elif value.lower() in ["deny", "skip", "exclude"]:  # Deny
                                dns_record.filter_type = 0
                            else:  # Off
                                dns_record.filter_type = -1
                        case "ip_type":
                            dns_record.IP_type = value
    dnsapi = DNSAPICloudflare([])
    return dnsapi, dns_records
