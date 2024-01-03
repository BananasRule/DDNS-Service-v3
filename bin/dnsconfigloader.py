## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.


import dnsapicloudflare
import dnsapiinterface


## A factory for creating the correct DNSAPI class and associated objects
# @param config An list containing all lines in the DNS configuration section
def dnsconfigloader(config: [str], variables: {str: str}) -> [dnsapiinterface.DNSAPIInterface,
                                                              [dnsapiinterface.DomainInfo]]:
    dns_api = None
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
                        dns_api, domains_info = dnsapicloudflare.cloudflarednsconfigloader(config, variables)

    return dns_api, domains_info

