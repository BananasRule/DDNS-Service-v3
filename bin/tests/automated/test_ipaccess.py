import unittest
import requests
from bin.ipaccess import GetIP


class TestIPAccess(unittest.TestCase):

    # Test case to determine that the ip access service works correctly
    def testipauto(self):
        # Test ipify
        service = GetIP("https://api.ipify.org", "https://api.ipify.org")
        ipify_output = service.get()
        self.assertEqual(requests.get("https://api.ipify.org").content.decode("utf-8").strip(), ipify_output,
                         "Incorrect output with ipify")

        # Test curl my ip
        service = GetIP("https://curlmyip.net/", "https://curlmyip.net/")
        curlip_output = service.get()
        self.assertEqual(requests.get("https://curlmyip.net/").content.decode("utf-8").strip(), curlip_output,
                         "Incorrect output with curl my ip")

        # Test that IP outputs match
        self.assertEqual(ipify_output, curlip_output, "IP addresses don't match" + ipify_output + ", " + curlip_output)
        print("OUTPUT OF IP ACCESS : " + ipify_output)

