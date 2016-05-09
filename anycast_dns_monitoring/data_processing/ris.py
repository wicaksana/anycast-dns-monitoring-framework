import requests
from pymongo import MongoClient
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.node import Node
from anycast_dns_monitoring.data_processing.encoder import Encoder

class Ris:
    """
    get control-plane data
    https://stat.ripe.net/docs/data_api
    ?? https://stat.ripe.net/data/looking-glass/data.json?resource=140.78.0.0/16
    """
    def __init__(self):
        self.db = self._initiate_db()

    def _initiate_db(self):
        """
        initiate connection to mongodb
        :return: db
        """
        client = MongoClient()
        db = client[params.db]
        return db

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

    def get_data(self, par):
        """
        output example: [{'as_path': ['15547', '8220', '1853', '1205'], 'rrc': 'RRC04'}]
        :param par:
        :return:
        """
        uri = '{0}looking-glass/data.json?resource={1}'.format(params.ris_uri, par)
        data = requests.get(uri).json()['data']
        result = []

        for rrc in data['rrcs']:
            for peer in data['rrcs'][rrc]['entries']:
                path = peer['as_path'].strip().split(' ')
                path.append(' ') # for the sake of tree creation code
                result.append(path)
        return result

    def tree_control_plane(self):
        """
        send data for control-plane tree visualization
        :return:
        """
        data = self.get_data(params.prefix)
        root_list = []

        for as_path in data:
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
                        cur_node = cur_node.add_child(node, [])
                    else:
                        cur_node = cur_node.add_child(node)
                level += 1

        result = Encoder().encode(root_list)[1:-1]
        return result
