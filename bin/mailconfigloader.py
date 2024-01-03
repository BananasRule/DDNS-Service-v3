## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.


import logging

import commonexception as comex
from mailservice import MailService, DummyMailService


## Exception class for mail misconfiguration
class MailError(Exception):
    pass


## Function to record logg a fatal error and then raise the Fatal Error exception
# @param logger Logger to use to record the error
# @param message Message to log
# @throws MailError
def log_mail_error(logger, message):
    logger.warning(message)
    raise MailError


## Function to call mail error and log


## Function to create the mail service from a config file
# @param config List of strings
# @param variables Dictionary of variables
def mailconfigloader(config: [str], variables: {str: str}) -> MailService:
    logger = logging.getLogger(__name__)

    # Variables for object creation
    server = None
    port = None
    tls = None
    ssl = None
    from_address = None
    to_address = None
    key = None
    secret = None
    send_ip = None

    for line in config:
        # Split into setting and value
        setting, value = line.split("=", 1)
        # Check if the value is a variable, and replace it with the var
        if value[0] == "$":
            if value[1:] in variables:
                value = variables[value]
            else:
                comex.log_fatal(logger, "Variable used without assignment. Program will now terminate.")

        match setting:
            case "server":
                server = value
            case "port":
                try:
                    port = int(value)
                except ValueError:
                    logger.warning("Port setting not convertible to int.")
            case "tls":
                if value.lower() == "true":
                    tls = True
                elif value.lower() == "false":
                    tls = False
            case "ssl":
                if value.lower() == "true":
                    ssl = True
                elif value.lower() == "false":
                    ssl = False
            case "from_address":
                from_address = value
            case "to_address":
                to_address = value
            case "key":
                key = value
            case "secret":
                secret = value
            case "send_ip":
                if value.lower() == "true":
                    send_ip = True
                elif value.lower() == "false":
                    send_ip = False

    # Check settings
    try:
        # Check server is set
        if server is None:
            log_mail_error(logger, "No server configured. Mail Service will not function.")

        # Check port is set
        if port is None:
            log_mail_error(logger, "No port configured. Mail Service will not function.")

        # Check encryption scheme exists
        if tls is None and ssl is None:
            logger.error("Encryption scheme is not specified. Defaulting to none.")
            tls = False
            ssl = False
        # If both schemes are off, log as not recommended
        elif not tls and not ssl:
            logger.info("Encryption scheme is not enable. This is not recommended.")

        # Check addresses
        if from_address is None or to_address is None:
            log_mail_error(logger, "Mail addresses not specified. Mail Service will not function.")

        # Check key
        if key is None:
            log_mail_error(logger, "Server Key not specified. Mail Service will not function.")

        # Check secret
        if secret is None:
            log_mail_error(logger, "Server Secret not specified. Mail Service will not function.")

        # Check send_ip - default to off
        if send_ip is None:
            logger.info("Send IP not set, defaulting to off.")
            send_ip = False
    # If there was a setting error, return the dummy mail object
    except MailError:
        mail_service = DummyMailService()
    else:
        mail_service = MailService(server, port, key, secret, tls, ssl, from_address, to_address, send_ip)

    return mail_service
