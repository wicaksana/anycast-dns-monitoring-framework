import unittest
from anycast_dns_monitoring.data_processing.cymru import get_asn
from anycast_dns_monitoring.data_processing.cymru import get_bulk_asn


class CymruTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_asn(self):
        result = get_asn('2001:948:1:e::2')
        print(result)

    def test_get_bulk_asn(self):
        prefix_list = ['167.205.79.1', '2403:8000::']
        result = get_bulk_asn(prefix_list)

        print(result)