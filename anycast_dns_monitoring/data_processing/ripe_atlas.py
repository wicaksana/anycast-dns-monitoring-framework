import requests
import ipaddress
from pprint import pprint
from pymongo import MongoClient
from anycast_dns_monitoring.data_processing.node import Node
from anycast_dns_monitoring.data_processing.encoder import Encoder
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.params import measurement_id, base_uri, RipeAtlasData


class RipeAtlas:
    def __init__(self):
        self.db = self._initiate_db()

    def _initiate_db(self):
        """

        :return: db
        """
        client = MongoClient()
        db = client[params.db]
        return db

    def _get_data(self, data_type, datetime=None):
        """
        get data from RIPE Atlas
        :return:
        """
        uri = ''
        if data_type == RipeAtlasData.traceroute:
            uri = '{0}measurement/{1}/result/?start={2}&stop={3}'\
                .format(base_uri, measurement_id, int(datetime) - 1200, datetime)
        results = requests.get(url=uri).json()
        return results

    def _get_asn(self, prefix):
        """
        query db to get ASN of a certain prefix
        :param prefix:
        :return:
        """
        query = {'prefix': prefix}
        result = self.db.prefix_asn_mapping.find_one(query)
        if result is None:
            return '0'

        return result['asn']

    def _get_probes_in_asn(self, asn):
        """
        get all probes in an ASN
        :return:
        """
        query = {'asn4': int(asn)}
        query_result = self.db.probes.find(query)
        result = []
        for res in query_result:
            result.append(res['prb_id'])

        return result

    def traceroute_data(self, datetime):
        """
        process traceroute data retrieved from RIPE Atlas
        :return:
        """
        traceroute_data = self._get_data(RipeAtlasData.traceroute, datetime=datetime)
        result = []

        for index, msmnt in enumerate(traceroute_data):
            path = []
            for result_per_probe in msmnt['result']:
                if 'from' in result_per_probe['result'][0]:  # at the moment, take care only the first result of traceroute
                    hop = result_per_probe['result'][0]['from']
                    hop_prefix = ipaddress.ip_interface(hop + '/24')
                    hop_prefix_str = str(hop_prefix.network).split('/24')[0]

                    # if the prefix is a public address and its ASN is not 0
                    if not hop_prefix.is_private:
                        asn = self._get_asn(hop_prefix_str)
                        if asn is not '0':
                            path.append(asn)

            result.append({})
            result[index]['prb_id'] = str(msmnt['prb_id'])
            result[index]['path'] = path

        return result

    def tree_data_plane(self, datetime):
        """
        get traceroute measurement for a certain time
        :return:
        """
        data = self.traceroute_data(datetime=datetime)

        root_list = []

        for probe in data:
            as_path = probe['path']
            as_path.reverse()

            level = 0
            cur_node = None

            for asn in as_path:
                if level == 0:
                    node = None
                    matching_nodes = [x for x in root_list if x.name == str(asn)]
                    if len(matching_nodes) > 0:
                        node = matching_nodes[0]
                    # the following is only applied during the first time of root node creation
                    if node is None:
                        node = Node(str(asn))
                        # node.probes.append(probe_id)
                        root_list.append(node)
                        # print("[0] node {} is appended to rootlist.".format(node.name))
                    cur_node = node
                else:
                    node = Node(str(asn))
                    if level == len(as_path) - 1:  # probe resides in the last element (ASN) of as_path
                        # node.probes.append(probe_id)
                        cur_node = cur_node.add_child(node, self._get_probes_in_asn(asn=asn))
                    else:
                        cur_node = cur_node.add_child(node)
                level += 1

        # print("var astree = " + Encoder().encode(root_list)[1:-1] + ";")
        # pprint(Encoder().encode(root_list)[1:-1])
        result = Encoder().encode(root_list)[1:-1]
        print(result)
        return result