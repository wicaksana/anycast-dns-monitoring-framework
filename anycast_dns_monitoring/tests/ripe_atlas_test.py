import unittest
from pprint import pprint
from anycast_dns_monitoring.data_processing.ripe_atlas import RipeAtlas
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.params import RipeAtlasData, Version


class RipeAtlasTest(unittest.TestCase):
    def setUp(self):
        self.ra = RipeAtlas(Version.ipv4)
        self.datetime = 1459948020 # UNIX timestamp of ground truth

    def test_get_data(self):
        # IPv4
        print('ipv4: ')
        print(self.ra._get_data(id=params.msmnt_id, data_type=RipeAtlasData.traceroute, datetime=self.datetime))

        # IPv6
        print('ipv6: ')
        pprint(self.ra._get_data(id=params.msmnt_id6, data_type=RipeAtlasData.traceroute, datetime=1462797042))

    def test_get_asn(self):
        self.assertEqual(self.ra._get_asn('50.196.164.0'), '33651')

    def test_get_probes_in_asn(self):
        self.assertEqual(self.ra._get_probes_in_asn('378'), [17832, 17846, 17875])

    def test_get_probes_v6_in_asn(self):
        # self.assertEqual(self.ra._get_probes_in_asn('378'), [17832, 17846, 17875])
        print(self.ra._get_probes_v6_in_asn(''))

    def test_traceroute_data(self):
        # ipv4
        # result1 = self.ra.traceroute_data(datetime=self.datetime, version=params.Version.ipv4)
        # print(result1)

        # ipv6
        self.ra = RipeAtlas(Version.ipv6)
        result2 = self.ra.traceroute_data(datetime=1462797042)
        print(result2)

    def test_tree_data_plane(self):
        self.ra.tree_data_plane(datetime=self.datetime)

