import unittest
from anycast_dns_monitoring.data_processing.ripe_atlas import RipeAtlas
from anycast_dns_monitoring.data_processing.params import RipeAtlasData

class RipeAtlasTest(unittest.TestCase):
    def setUp(self):
        self.ra = RipeAtlas()
        self.datetime = 1459948020 # UNIX timestamp of ground truth

    def test_get_data(self):
        print(self.ra._get_data(datetime=self.datetime, data_type=RipeAtlasData.traceroute))

    def test_get_asn(self):
        self.assertEqual(self.ra._get_asn('50.196.164.0'), '33651')

    def test_get_probes_in_asn(self):
        self.assertEqual(self.ra._get_probes_in_asn('378'), [17832, 17846, 17875])

    def test_traceroute_data(self):
        result = self.ra.traceroute_data(datetime=self.datetime)
        print(result)

    def test_tree_data_plane(self):
        self.ra.tree_data_plane(datetime=self.datetime)
