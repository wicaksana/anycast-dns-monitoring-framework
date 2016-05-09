import unittest
from pprint import pprint
from anycast_dns_monitoring.data_processing.ris import Ris


class RisTest(unittest.TestCase):
    def setUp(self):
        self.ris = Ris()
        self.prefix = '140.78.0.0/16'

    def test_get_data(self):
        res = self.ris.get_data(self.prefix)
        # for rrc in res['rrcs']:
        #     print(res['rrcs'][rrc]['entries'][0]['as_path'])
        pprint(res)

        # print('\nno data:')
        # for rrc in res['no_data_rrcs']:
        #     print(rrc['rrc'])

        # pprint(res)