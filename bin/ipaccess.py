## © Jacob Gray 2024
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.


import logging
import time
import requests
import commonexception


## GetIP class enables access to a server to determine the current public IP address
class GetIP:

    ## Create the GetIP object
    # @param primary_server_url The primary server used to get the current public IP. Must return text.
    # @param fallback_server_url The fallback server used to get the current public IP. Must return text.
    def __init__(self, primary_server_url: str, fallback_server_url: str):
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._primary_server_url: str = primary_server_url
        self._fallback_server_url: str = fallback_server_url
        self.logger.debug("Created GetIP class")

    ## Get the server's current public IP address
    # @returns Current IP address in plain text
    # @throws FatalError IP address not obtainable
    def get(self) -> str:
        success = False
        response = None
        # Attempt to get IP address from primary server
        # noinspection PyBroadException
        # Broad exception allows for a potential recovery
        try:
            response = requests.get(self._primary_server_url)
            response.raise_for_status()
            success = True

        except requests.ConnectionError or requests.Timeout:
            self.logger.warning("Error with primary IP address server. Error connecting to server. \
                                Attempting to access fallback server in 30 seconds")
        # Except an incorrect response
        except requests.HTTPError:
            self.logger.warning("Error with primary IP address server. A response code other than 200 was received. \
                                Attempting to access fallback server in 30 seconds")

        # Attempt to recover from other errors
        except Exception:
            self.logger.warning("Error with primary IP address server. An unknown error has occurred. \
                                Attempting to access fallback server in 30 seconds")

        # If an IP address was not obtained from the primary server, attempt to obtain one from the fallback server
        if not success:
            # Wait in case of a temporary network connectivity issue
            time.sleep(30)
            try:
                # Attempt to get IP from fallback server
                response = requests.get(self._fallback_server_url)
                if response.status_code != 200:
                    raise _GetIPResponseError
                else:
                    success = True

            # Except an incorrect response
            except _GetIPResponseError:
                self.logger.critical("Error with fallback IP address server. A response code other than 200 was \
                                        received. Application will exit.")

        # Check an ip address was received
        if success:
            ip_address = response.content.decode("utf-8").strip()
            self.logger.debug("IP Address received")
        else:
            # If not raise error
            raise commonexception.FatalError("An unrecoverable error occurred while retrieving the servers IP address")

        return ip_address


## Error class for response errors
class _GetIPResponseError(Exception):
    pass
