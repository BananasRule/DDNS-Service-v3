## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.


import commonexception as comex
import logging
from ipaccess import GetIP


def ipconfigloader(config: [str], variables: {str: str}) -> [GetIP, GetIP]:
    # Get logger
    logger = logging.getLogger(__name__)

    ipv4 = [None, None]
    ipv6 = [None, None]

    ipv4_service = None
    ipv6_service = None

    for line in config:
        setting, value = line.split("=", 1)
        # Check if the value is a variable, and replace it with the var
        if value[0] == "$":
            if value[1:] in variables:
                value = variables[value[1:]]
            else:
                comex.log_fatal(logger, "Variable used without assignment. Program will now terminate.")

        match setting:
            case "IPv4_Primary":
                ipv4[0] = value
            case "IPv4_Fallback":
                ipv4[1] = value
            case "IPv6_Primary":
                ipv6[0] = value
            case "IPv6_Fallback":
                ipv6[1] = value

    if ipv4[0] is not None:
        if ipv4[1] is not None:
            ipv4_service = GetIP(ipv4[0], ipv4[1])
        else:
            ipv4_service = GetIP(ipv4[0], ipv4[0])
            logger.warning("IPv4 fallback server undefined.")

    if ipv6[0] is not None:
        if ipv6[1] is not None:
            ipv6_service = GetIP(ipv6[0], ipv6[1])
        else:
            ipv6_service = GetIP(ipv6[0], ipv6[0])
            logger.warning("IPv6 fallback server undefined.")

    return ipv4_service, ipv6_service
