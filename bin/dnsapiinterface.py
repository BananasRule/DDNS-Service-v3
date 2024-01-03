## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.

## Template class to store domain attributes
class DomainInfo:
    def __init__(self):
        raise NotImplementedError("Abstract DomainInfo class created")


## Template class to store record attributes
class RecordInfo:
    def __init__(self):
        self.record_name: str
        self.IP_address: str
        raise NotImplementedError("Abstract RecordInfo class created")


## Concrete class to store outcome of DNS updates
class UpdateInfo:
    def __init__(self):
        self.success: [str] = []
        self.failure: [str] = []


## Concrete class to store combined domain and corresponding record info
class DomainRecords:
    def __init__(self, domaininfo: DomainInfo, recordsinfo: [RecordInfo]):
        self.domain: DomainInfo = domaininfo
        self.records: [RecordInfo] = recordsinfo



## @interface
class DNSAPIInterface:

    ## A generic initialisation
    # @param apiinfo List customised for each provider
    def __init__(self, apiinfo: [any]):
        raise NotImplementedError("Abstract DNSAPI class created")

    ## Function to return all records found using domaininfo
    # @param domaininfo A object of a concrete _DomainInfo class
    # @returns recordinfo List of domain information structured as such [domainname, ipaddress, otherattributes]
    def get_records(self, domaininfo: DomainInfo):
        raise NotImplementedError("Abstract DNSAPI class called")

    ## Function to update all records in a single recordinfo
    # @param recordinfo An object of a concrete _RecordInfo class
    # @throws UpdateError Error indicating an error occurred during record update
    def update(self, recordinfo: RecordInfo, ipaddress: str, domaininfo: DomainInfo) -> None:
        raise NotImplementedError("Abstract DNSAPI class called")

    ## Function to get all records for all domains
    # @param domainsinfo An List of concrete _DomainInfo type
    # @returns recordsinfo Object of DomainRecord type
    def get_all_records(self, domainsinfo: [DomainInfo]) -> [DomainRecords]:
        raise NotImplementedError("Abstract DNSAPI class called")

    def multi_update(self, recordsinfo: [RecordInfo], domaininfo: DomainInfo, currentIP: str) -> UpdateInfo:
        raise NotImplementedError("Abstract DNSAPI class called")

## Class for an update error
class UpdateError(Exception):
    pass
