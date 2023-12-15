import bin.dnsapicloudflare as dnsapiclass
from bin.dnsapi_interface import _DNSAPI_Interface


def get_test():
    config = []
    with open("dnsapi_cloudflare_config.secret") as configfile:
        config = configfile.read().splitlines()

    domain = dnsapiclass.CloudflareDomainInfo(config[1], config[0], "A")
    dnsapi = dnsapiclass.DNSAPICloudflare([])
    records = dnsapi.get_records(domain)
    allrecords = dnsapi.get_all_records([domain])
    print(records)

def patch_test():
    config = []
    with open("dnsapi_cloudflare_config.secret") as configfile:
        config = configfile.read().splitlines()

    domain = dnsapiclass.CloudflareDomainInfo(config[1], config[0], "A")
    dnsapi = dnsapiclass.DNSAPICloudflare([])
    records = dnsapi.get_records(domain)
    allrecords = dnsapi.get_all_records([domain])
    updatestatus = dnsapi.multi_update(allrecords[0][1], allrecords[0][0], "220.235.120.26")
    pass

patch_test()