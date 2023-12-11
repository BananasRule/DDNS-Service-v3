from bin.dnsapi_interface import _DNSAPI_Interface
import logging
import requests


class DNSAPI_Cloudflare(_DNSAPI_Interface):
    ## Create a DNSAPI Cloudflare variation object
    # @param apiinfo Array [apitoken]
    def __init__(self, discard):
        self.logger = logging.getLogger(__name__)

    ## Function to return all records found using domaininfo
    # @param domaininfo Array [zoneid, zoneapikey, iptype]
    # @returns recordinfo Array of domain information structured as such [domainname, ipaddress, otherattributes]
    def get_records(self, domaininfo):
        requestparams = {"type": domaininfo[2]}
        requestheaders = {"Authorization": ("Bearer " + domaininfo[1]), "Content-Type": "application/json"}
        response = requests.get("https://api.cloudflare.com/client/v4/zones/" + domaininfo[0] + "/dns_records",
                                headers=requestheaders, params=requestparams)
        records = response.json()["result"]
        recordinfo = []
        for record in records:
            domainid = record["id"]
            domainname = record["name"]
            ipaddress = record["content"]
            recordinfo.append([domainid, domainname, ipaddress,])
        return recordinfo
