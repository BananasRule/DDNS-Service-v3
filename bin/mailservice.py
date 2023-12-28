import smtplib
import datetime


class MailService:

    ## Initialise object
    # @param server Server web address (String)
    # @param port Server SMTP port (Int)
    # @param key API Key / Username (String)
    # @param secret API Secret / Password (String)
    # @param tls Use TLS (Bool)
    # @param ssl Use SSL (Bool)
    # @param fromAddress The address the message will be sent from (String)
    # @param toAddress The address the message will be sent to (String)
    def __init__(self, server: str, port: int, key: str, secret: str, tls: bool, ssl: bool,
                 from_address: str, to_address: str, send_ip: bool):
        self.partHeader = "To:" + to_address + "\nFrom:" + from_address + "\n"
        self.server = server
        self.port = port
        self.key = key
        self.secret = secret
        self.tls = tls
        self.ssl = ssl
        self.from_address = from_address
        self.to_address = to_address
        self.send_IP = send_ip

    ## Function used to send messages
    # @param subject The message subject
    # @param message The message to send
    def send(self, subject, message):
        # Create header and message to send
        header = self.partHeader + "Subject:" + subject + "\n"
        msg = header + message

        # Connect to server
        if self.ssl:
            mailserver = smtplib.SMTP_SSL(self.server, self.port)
        else:
            mailserver = smtplib.SMTP(self.server, self.port)

        # If TLS is enabled and SSL is not
        if self.tls and not self.ssl:
            mailserver.starttls()
            mailserver.ehlo()

        # Login to mail server
        mailserver.login(self.key, self.secret)

        # Send message
        mailserver.sendmail(self.from_address, self.to_address, msg)

        # Close connection
        mailserver.quit()

    # noinspection PyMethodMayBeStatic
    # Easier to use and implement when part of class
    ## Compose message to send
    # @param zoneName The name of the zone updated
    # @param successUpdate An list containing the ID of successfully updated zones (List)
    # @param failedUpdate An list containing the ID of zones that failed to update (List)
    # @param previousMessage The previous message composed (default to "") (String)
    # @returns Message to be passed to Send module
    def compose(self, success_update: [str], failed_update: [str], zone_name: str, previous_message: str = "") -> str:
        message = previous_message
        if len(success_update) != 0 or len(failed_update) != 0:
            message = message + zone_name + "\n"
            # Loop through each successful update message if at least one exists
            if len(success_update) != 0:
                # Add header message
                message = message + "   The following domains successfully updated:\n"
                # Loop through zones listing zone and IDs
                for record in success_update:
                    # Shouldn't occur but to catch a blank zone anyway
                    if len(record) != 0:
                        message = message + "       " + record + "\n"

            # Loop through each failed update message if at least one exists
            if len(failed_update) != 0:
                # Add header message
                message = message + "   The following domains failed to update:\n"
                # Loop through zones listing zone and IDs
                for record in failed_update:
                    # Shouldn't occur but to catch a blank zone anyway
                    if len(record) != 0:
                        message = message + "       " + id + "\n"
        # Return message
        return message

    def footer(self, message: str, current_ip: str):
        # Add blank line
        message = message + "\n"
        # If sendIP address is true send the current IP address
        if self.send_IP:
            message = message + "The servers current IP address is: " + current_ip + ".\n"

        # Append date and time to message
        message = message + "This message was sent on " + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + "."
        return message


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
# Dummy class designed to do nothing
## A class when the normal mail class cannot be loaded
# It won't send emails but will allow the program to function normally
class DummyMailService:

    def send(self, subject, message):
        pass

    def compose(self, success_update: [str], failed_update: [str], previous_message: str = ""):
        return "MAIL NOT CONFIGURED"

    def footer(self, message: str, current_ip: str):
        return message
