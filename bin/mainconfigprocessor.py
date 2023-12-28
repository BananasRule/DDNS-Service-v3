import logging
import commonexception as comex
from bin import dnsconfigloader
from bin import mailconfigloader
from bin import ipconfigloader
from bin import ipaccess
from bin import mailservice
from bin import dnsapiinterface


class AppletBlock:
    ipv4_service: ipaccess.GetIP = None
    ipv6_service: ipaccess.GetIP = None
    mail_service: mailservice.MailService | mailservice.DummyMailService = None
    domain_records: [dnsapiinterface.DomainRecords] = None
    dns_api: dnsapiinterface.DNSAPIInterface = None


def mainconfigloader() -> AppletBlock:
    logger = logging.getLogger(__name__)
    # Load config
    configfile = open("../config/config.conf")

    # Supported config version
    configver = "1"

    # Define file command characters
    metadata = "*"
    variabledef = "@"
    zonebound = "!"

    # Load variables
    variables = {}
    for line in configfile:
        # Remove comments
        line = line.split("#")[0]
        # Remove whitespace
        line = line.strip()

        # Check for empty lines
        if len(line) > 0:
            commandchar = line[0]
            if commandchar == variabledef:
                if line[1] == "$":
                    varpair = line[2:].split("=", 1)
                    variables[varpair[0]] = varpair[1]

    # Variables to determine where to save config
    mailarea = False
    dnsarea = False
    iparea = False

    # Separate config into separate parts
    dnsconfig = []
    mailconfig = []
    ipconfig = []
    programconfig = []

    configfile.seek(0)
    # Load config
    for line in configfile:
        # Remove comments
        line = line.split("#")[0]
        # Remove whitespace
        line = line.strip()
        line = line.replace(" ", "")

        if len(line) > 0:
            commandchar = line[0]
            # Check that config version matches
            if commandchar == metadata:
                setting, value = line[1:].split("=")
                if setting == "configversion":
                    if value != configver:
                        comex.log_fatal(logger, "Config version does not match config loader version. "
                                                "Program will now terminate.")

            # Ignore variable definitions
            elif commandchar == variabledef:
                pass
            # Set the zone of config
            elif commandchar == zonebound:
                # Exclude DNS zones
                if (line == "!ZONE" or line == "!!ZONE") and dnsarea:
                    dnsconfig.append(line)
                else:
                    # Check if starting or ending a zone
                    if line[1] == zonebound:
                        line = line[2:]
                        # Check zone to close
                        if line == "DNSCONFIG":
                            # Check that zone was open, raise error if it wasn't
                            if not dnsarea:
                                comex.log_fatal(logger, "Error in zone definitions. "
                                                        "DNSCONFIG was closed before it was opened. "
                                                        "Program will now terminate.")
                            else:
                                dnsarea = False
                        elif line == "MAILCONFIG":
                            # Check that zone was open, raise error if it wasn't
                            if not mailarea:
                                comex.log_fatal(logger, "Error in zone definitions. "
                                                        "MAILCONFIG was closed before it was opened. "
                                                        "Program will now terminate.")
                            else:
                                mailarea = False
                        elif line == "IPCONFIG":
                            # Check that zone was open, raise error if it wasn't
                            if not iparea:
                                comex.log_fatal(logger, "Error in zone definitions. "
                                                        "MAILCONFIG was closed before it was opened. "
                                                        "Program will now terminate.")
                            else:
                                iparea = False

                    else:
                        # The first ! was already checked, and so this is opening a zone
                        line = line[1:]
                        if line == "DNSCONFIG":
                            # Check that conflicting zone isn't open
                            if mailarea:
                                comex.log_fatal(logger, "Error in zone definitions. Conflicting zones. "
                                                        "Program will now terminate.")
                            # Check that zone isn't already open
                            elif dnsarea or iparea:
                                comex.log_fatal(logger, "Error in zone definitions. "
                                                        "DNSCONFIG opened while already open. "
                                                        "Program will now terminate.")
                            else:
                                dnsarea = True
                        elif line == "MAILCONFIG":
                            # Check that zone isn't already open
                            if mailarea:
                                comex.log_fatal(logger, "Error in zone definitions. "
                                                        "MAILCONFIG opened while already open. "
                                                        "Program will now terminate.")
                            # Check that conflicting zone isn't open
                            elif dnsarea or iparea:
                                comex.log_fatal(logger, "Error in zone definitions. Conflicting zones. "
                                                        "Program will now terminate.")
                            else:
                                mailarea = True
                        elif line == "IPCONFIG":
                            # Check that zone isn't already open
                            if iparea:
                                comex.log_fatal(logger, "Error in zone definitions. "
                                                        "MAILCONFIG opened while already open. "
                                                        "Program will now terminate.")
                            # Check that conflicting zone isn't open
                            elif dnsarea or mailarea:
                                comex.log_fatal(logger, "Error in zone definitions. Conflicting zones. "
                                                        "Program will now terminate.")
                            else:
                                iparea = True
            else:
                if dnsarea:
                    dnsconfig.append(line)
                elif mailarea:
                    mailconfig.append(line)
                elif iparea:
                    ipconfig.append(line)
                else:
                    programconfig.append(line)

    # Call loaders for services and add to applet block
    applet_block = AppletBlock()
    applet_block.dns_api, applet_block.domain_records = dnsconfigloader.dnsconfigloader(dnsconfig, variables)
    applet_block.mail_service = mailconfigloader.mailconfigloader(mailconfig, variables)
    applet_block.ipv4_service, applet_block.ipv6_service = ipconfigloader.ipconfigloader(ipconfig, variables)

    return applet_block
