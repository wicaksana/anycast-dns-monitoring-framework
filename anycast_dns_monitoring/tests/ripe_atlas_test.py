import unittest
import os
from pprint import pprint
from anycast_dns_monitoring.data_processing.ripe_atlas import RipeAtlas
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.params import RipeAtlasData, Version


class RipeAtlasTest(unittest.TestCase):
    def setUp(self):
        self.ra = RipeAtlas(Version.ipv4)
        self.ra2 = RipeAtlas(Version.ipv6)
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

    def test_get_probes6_in_asn(self):
        result = self.ra._get_probes6_in_asn(3215)
        self.assertEqual(result, [17039, 17123, 17220])

    def test_traceroute4_data(self):
        # ipv4
        result1 = self.ra._traceroute4_data(datetime=self.datetime)
        print(result1)

        # ipv6
        # result2 = self.ra2.traceroute_data(datetime=1462797042)
        # print(result2)

    def test_traceroute6_data(self):
        result = self.ra2._traceroute6_data(datetime=1462797042)
        print(result)
        # assert os.path.exists('../data_processing/temp.txt')  # file should exist
        # assert os.stat('../data_processing/temp.txt').st_size is not 0  # file should not empty


    def test_tree_data_plane(self):
        self.ra.tree_data_plane(datetime=self.datetime)

    # TODO: create unittest for traceroute_data()
