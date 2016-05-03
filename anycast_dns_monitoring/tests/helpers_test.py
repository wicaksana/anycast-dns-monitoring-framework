import unittest
import requests
from anycast_dns_monitoring.data_processing.helpers import get_probe_list
from anycast_dns_monitoring.data_processing.helpers import get_bulk_asn
from anycast_dns_monitoring.data_processing.helpers import get_ip_asn_of_probe
from anycast_dns_monitoring.data_processing.helpers import get_prefix_to_asn


class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.measurement_id = '2048556'
        self.num_probes = 100

    def test_get_probe_list(self):
        """
        there are 100 probes used.
        :return:
        """
        result = get_probe_list(self.measurement_id)
        self.assertEqual(len(result), self.num_probes)

    def test_get_bulk_asn(self):
        pass

    def test_get_ip_asn_of_probe(self):
        result = get_ip_asn_of_probe(10151)
        self.assertEqual(get_ip_asn_of_probe(10151), ('86.176.241.135', None, 2856, None))

    def test_get_prefix_to_asn(self):
        result = get_prefix_to_asn()
        print(result)