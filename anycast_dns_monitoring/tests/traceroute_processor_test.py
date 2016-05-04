import unittest
import requests
from anycast_dns_monitoring.data_processing.traceroute_processor import TracerouteProcessor

dummy_msmt_data = [{'dst_addr': '204.9.168.1', 'result': [{'hop': 1, 'result': [{'rtt': 0.671, 'size': 28, 'ttl': 64, 'from': '192.168.0.1'}, {'rtt': 0.554, 'size': 28, 'ttl': 64, 'from': '192.168.0.1'}, {'rtt': 0.528, 'size': 28, 'ttl': 64, 'from': '192.168.0.1'}]}, {'hop': 2, 'result': [{'x': '*'}, {'x': '*'}, {'x': '*'}]}, {'hop': 3, 'result': [{'rtt': 10.103, 'size': 68, 'ttl': 253, 'from': '84.116.25.113'}, {'rtt': 9.818, 'size': 68, 'ttl': 253, 'from': '84.116.25.113'}, {'rtt': 7.456, 'size': 68, 'ttl': 253, 'from': '84.116.25.113'}]}, {'hop': 4, 'result': [{'x': '*'}, {'x': '*'}, {'x': '*'}]}, {'hop': 5, 'result': [{'x': '*'}, {'x': '*'}, {'x': '*'}]}, {'hop': 6, 'result': [{'x': '*'}, {'x': '*'}, {'x': '*'}]}, {'hop': 7, 'result': [{'x': '*'}, {'x': '*'}, {'x': '*'}]}, {'hop': 8, 'result': [{'x': '*'}, {'x': '*'}, {'x': '*'}]}, {'hop': 255, 'result': [{'x': '*'}, {'x': '*'}, {'x': '*'}]}], 'prb_id': 13919, 'paris_id': 3, 'proto': 'ICMP', 'type': 'traceroute', 'dst_name': '204.9.168.1', 'fw': 4730, 'endtime': 1459849025, 'timestamp': 1459848941, 'msm_id': 2048556, 'size': 48, 'group_id': 2048556, 'msm_name': 'Traceroute', 'af': 4, 'from': '80.108.219.71', 'src_addr': '192.168.0.10', 'lts': 1}]

class TracerouteProcessorTest(unittest.TestCase):
    def setUp(self):
        uri = 'https://atlas.ripe.net/api/v1/measurement/2048556/result/?start=1459946820&stop=1459948020'
        data = requests.get(url=uri).json()
        # self.tp = TracerouteProcessor(dummy_msmt_data)
        self.tp = TracerouteProcessor(data, 1459948020)

    def test_get_traceroute_data(self):
        result = self.tp.get_traceroute_data()
        print(result)
        # self.assertEqual(len(result[13919]), 9) # the resulted path should contain 9 hops

    def test_process(self):
        result = self.tp.process()
        print(result)