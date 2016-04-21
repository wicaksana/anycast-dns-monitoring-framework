import unittest
from pprint import pprint
from python_code.anycast_data_processing.traceroute_as_hop import *


class TracerouteAsHopTest(unittest.TestCase):
    def setUp(self):
        self.peering_asn = '47065'
        self.probe_as_list = "../../datasets/prb_as"
        self.prefix_as_list = "../../datasets/block_to_as_summary"
        self.probe_list = "../../datasets/prb_id_list"
        self.ripe_atlas_data = "../../datasets/201602070600.json"

        self.probe_as = get_probe_as(self.probe_as_list)
        self.prefix_as = get_prefix_to_as(self.prefix_as_list)
        self.probe_list = get_probe_list(self.probe_list)
        self.traceroute_data = get_traceroute_data(self.ripe_atlas_data)
        # probes_asn_path_list = get_asn_path(self.peering_asn, probe_list, prefix_as, traceroute_data)

    # def test_get_probe_as(self):
    #     self.assertIsNotNone(get_probe_as(self.probe_as_list))
    #
    # def test_get_prefix_to_as(self):
    #     self.assertIsNotNone(get_prefix_to_as(self.prefix_as_list))
    #
    # def test_get_probe_list(self):
    #     # print(get_probe_list(self.probe_list))
    #     self.assertIsNotNone(get_probe_list(self.probe_list))

    # def test_get_traceroute_data(self):
    #     self.assertIsNotNone(get_traceroute_data(self.ripe_atlas_data))

    def test_get_asn_path(self):
        # self.assertEqual(self.prefix_as['223.255.235.0'], 17766)
        output = get_asn_path(self.peering_asn,
                              self.probe_list,
                              self.prefix_as,
                              self.traceroute_data)
        pprint(output)
