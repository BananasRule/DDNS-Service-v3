import logging


## Template class to store domain attributes
class _DomainInfo:
    def __init__(self):
        raise NotImplementedError("Abstract DomainInfo class created")

## Template class to store record attributes
class _RecordInfo:
    def __init__(self, recordname: str, ipaddress: str):
        self.recordname = recordname
        self.ipaddress = ipaddress
        raise NotImplementedError("Abstract RecordInfo class created")


## Concrete class to store outcome of DNS updates
class UpdateInfo:
    def __init__(self):
        self.success = []
        self.failure = []

## Concrete class to store combined domain and corresponding record info
class DomainRecords:
    def __init__(self, domaininfo: _DomainInfo, recordsinfo: [_RecordInfo]):
        self.domain = domaininfo
        self.records = recordsinfo


## @interface
class _DNSAPI_Interface():

    ## A generic initialisation
    # @param apiinfo Array customised for each provider
    def __init__(self, apiinfo: [any]):
        raise NotImplementedError("Abstract DNSAPI class created")

    ## Function to return all records found using domaininfo
    # @param domaininfo A object of a concrete _DomainInfo class
    # @returns recordinfo Array of domain information structured as such [domainname, ipaddress, otherattributes]
    def get_records(self, domaininfo: _DomainInfo):
        raise NotImplementedError("Abstract DNSAPI class called")

    ## Function to update all records in a single recordinfo
    # @param recordinfo An object of a concrete _RecordInfo class
    # @returns recordupdateinfo Array containing fate of all attempted updates [succeeded, failed]
    def update(self, recordinfo: _RecordInfo, ipaddress: str, domaininfo: _DomainInfo):
        raise NotImplementedError("Abstract DNSAPI class called")

    ## Function to get all records for all domains
    # @param domainsinfo An Array of concrete _DomainInfo type
    # @returns recordsinfo Object of DomainRecord type
    def get_all_records(self, domainsinfo: [_DomainInfo]):
        raise NotImplementedError("Abstract DNSAPI class called")

    def multi_update(self, recordsinfo: [_RecordInfo], domaininfo: _DomainInfo, currentIP: str):
        raise NotImplementedError("Abstract DNSAPI class called")

