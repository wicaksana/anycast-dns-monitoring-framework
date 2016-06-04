import unittest
from pprint import pprint
from anycast_dns_monitoring.data_processing.ris import Ris
import anycast_dns_monitoring.data_processing.params as params


class RisTest(unittest.TestCase):
    def setUp(self):
        self.ris = Ris(params.Version.ipv4)
        self.prefix = '140.78.0.0/16'

    # def test_get_data(self):
    #     res = self.ris._get_data(self.prefix, 1462966967)
    #     pprint(res)

    def test_tree_control_plane(self):
        # test latest data
        print("test using the latest data...")
        res = self.ris.tree_control_plane()
        print(res)

        # test on some point in the past
        print("test using data from the past...")
        res2 = self.ris.tree_control_plane(1462966967)
        print(res2)