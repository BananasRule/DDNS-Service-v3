from bin import dnsapicloudflare
from bin import dnsapiinterface
## A factory for creating the correct DNSAPI class and associated objects
# @param config An list containing all lines in the DNS configuration section


def dnsconfigloader(config: [str], variables: {str: str}) -> [dnsapiinterface.DNSAPIInterface,
                                                              [dnsapiinterface.DomainInfo]]:
    dnsapi = None
    domains_info = None
    # Iterate through config until the provider setting is found
    for line in config:
        if line[0:8] == "provider":
            # Split setting a validate name
            setting, value = line.split("=", 1)
            if setting == "provider":
                # Find a match from preconfigured providers
                match value.lower():
                    case "cloudflare":
                        dnsapi, domains_info = dnsapicloudflare.cloudflarednsconfigloader(config, variables)

    return dnsapi, domains_info

