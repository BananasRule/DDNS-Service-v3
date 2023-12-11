import logging

## @interface
class _DNSAPI_Interface():

    ## A generic initialisation
    # @param apiinfo Array customised for each provider
    def __init__(self, apiinfo):
        raise NotImplementedError("Abstract DNSAPI class created")

    ## Function to return all records found using domaininfo
    # @param domaininfo Domain information is customised for each provider
    # @returns recordinfo Array of domain information structured as such [domainname, ipaddress, otherattributes]
    def get_records(self, domaininfo):
        raise NotImplementedError("Abstract DNSAPI class called")

    ## Function to update all records in the recordinfo
    # @param recordinfo Array of domain information structured as such [domainname, ipaddress, otherattributes]
    # @returns recordupdateinfo Array containing fate of all attempted updates [succeeded, failed]
    def update(self, recordinfo):
        raise NotImplementedError("Abstract DNSAPI class called")
