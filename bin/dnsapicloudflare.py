from bin.dnsapi_interface import _DNSAPI_Interface, _DomainInfo, _RecordInfo, UpdateInfo, DomainRecords
import bin.commonexception as comex
import logging
import requests


## Class to store domain level details
# noinspection PyMissingConstructor
class CloudflareDomainInfo(_DomainInfo):
    def __init__(self, zoneid: str, zonekey: str, iptype: str, zonename: str, filter: [str], filtertype: int) -> None:
        self.filter = filter
        self.filtertype = filtertype
        self.zonename = zonename
        self.zoneid = zoneid
        self.zonekey = zonekey
        self.iptype = iptype


## Class to store record details
# noinspection PyMissingConstructor
class CloudflareRecordInfo(_RecordInfo):
    def __init__(self, recordname: str, ipaddress: str, recordid: str):
        self.recordname = recordname
        self.ipaddress = ipaddress
        self.recordid = recordid


# noinspection PyMissingConstructor
# Suppress naming for clarity - DNSAPICloudflare
## Main class implementing _DNSAPI_Interface() interface
# noinspection PyUnusedLocal
class DNSAPICloudflare(_DNSAPI_Interface):
    ## Create a DNSAPI Cloudflare variation object
    # @param apiinfo Array [apitoken]
    def __init__(self, discard: [any]):
        self.logger = logging.getLogger(__name__)

    ## Function to return all records found using domaininfo
    # @param domaininfo Object of CloudflareDomainInfo type
    # @returns recordinfo Array of objects of CloudflareRecordInfo type
    # @throws FatalError Unable to access API, program should terminate
    def get_records(self, domaininfo: CloudflareDomainInfo):
        # Create parameter for request
        requestparams = {"type": domaininfo.iptype}

        # Create Auth headers
        requestheaders = {
            "Authorization": ("Bearer " + domaininfo.zonekey),
            "Content-Type": "application/json"
        }

        # Create URL
        url = "https://api.cloudflare.com/client/v4/zones/" + domaininfo.zoneid + "/dns_records"

        # Attempt to execute request
        try:
            response = requests.get(url, headers=requestheaders, params=requestparams)
            response.raise_for_status()
        except requests.ConnectionError or requests.Timeout:
            # Except failure to connect
            comex.logfatal(self.logger, "Unable to connect to Cloudflare API during GET. " +
                                        "Program will now terminate.")
        except requests.HTTPError:
            # Except a non-200 status code
            comex.logfatal(self.logger, "Received invalid response from Cloudflare API during GET. " +
                                        "Program will now terminate.")
        else:
            # If request succeeds process into array of record objects
            records = response.json()["result"]
            recordinfo = []
            for record in records:
                domainid = record["id"]
                domainname = record["name"]
                ipaddress = record["content"]
                recordinfo.append(CloudflareRecordInfo(domainname, ipaddress, domainid))
            # Return array
            return recordinfo

    ## Function to operate with a list of all records
    # @param domainsinfo Array of CloudflareDomainInfo objects
    # @returns  Array of object of DomainRecord type
    def get_all_records(self, domainsinfo: [CloudflareDomainInfo]) -> [DomainRecords]:
        # Run on each domain and create a formatted list
        allrecords = []
        for domaininfo in domainsinfo:
            records = self.get_records(domaininfo)
            completerecord = DomainRecords(domaininfo, records)
            allrecords.append(completerecord)
        return allrecords

    ## Function to patch records with new IP address
    # @param domaininfo DomainInfo class object
    # @param recordinfo RecordInfo class object
    # @param currentIP Current IP address as a string
    def update(self, recordinfo: CloudflareRecordInfo, currentIP: str, domaininfo: CloudflareDomainInfo) -> None:
        # Create data for update
        data = {
            "content": currentIP,
            "name": recordinfo.recordname,
            "type": domaininfo.iptype
        }

        # Create Auth Headers
        requestheaders = {
            "Authorization": ("Bearer " + domaininfo.zonekey),
            "Content-Type": "application/json"
        }

        # Create URL
        url = ("https://api.cloudflare.com/client/v4/zones/" + domaininfo.zoneid + "/dns_records/" +
               recordinfo.recordid)

        # Attempt to issue patch request
        try:
            response = requests.patch(url, headers=requestheaders, json=data)
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
    # @param recordsinfo An array of RecordInfo class object
    # @param currentIP Current IP address as a string
    # @returns UpdateInfo object with statuses
    def multi_update(self, recordsinfo: [CloudflareRecordInfo], domaininfo: CloudflareDomainInfo, currentIP: str) \
            -> UpdateInfo:
        updateinfo = UpdateInfo()
        # Iterate through recordsinfo
        for recordinfo in recordsinfo:
            try:
                self.update(recordinfo, currentIP, domaininfo)
            except UpdateError:
                updateinfo.failure.append(recordinfo.recordname)
            else:
                updateinfo.success.append(recordinfo.recordname)
        return updateinfo


## Class for an update error
class UpdateError(Exception):
    pass
