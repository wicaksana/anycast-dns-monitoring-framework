import requests
import ipaddress
from pprint import pprint
from pymongo import MongoClient
from anycast_dns_monitoring.data_processing.node import Node
from anycast_dns_monitoring.data_processing.encoder import Encoder
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.params import RipeAtlasData, Version
from anycast_dns_monitoring.data_processing.params import atlas_uri, msmnt_id, msmnt_id6, peering_asn
import anycast_dns_monitoring.data_processing.cymru as cymru
from anycast_dns_monitoring.data_processing.db import Db

class RipeAtlas:
    """
    anything related to RIPE Atlas
    currently, data related to probes are pre-populated. It should be updated daily, or if there is any changes, this
    should support immediate update (add method to do that)
    """
    #TODO: IP version should be included as class property
    def __init__(self, ip_version):
        self.db = self._initiate_db()
        self.ip_version = ip_version

    def _initiate_db(self):
        """
        initiate connection to mongodb
        :return: db
        """
        client = MongoClient()
        db = client[params.db]

        return db

    def _get_data(self, data_type, id, datetime=None):
        """
        get data from RIPE Atlas
        :param id measurement id
        :param datetime
        :return:
        """
        uri = ''
        # get traceroute data
        if data_type == RipeAtlasData.traceroute:
            if self.ip_version is Version.ipv4:
                uri = '{0}measurement/{1}/result/?start={2}&stop={3}'\
                    .format(atlas_uri, id, int(datetime) - 1200, datetime)
            # TEMPORARY!! only because I use random measurement that use interval 300s
            else:
                uri = '{0}measurement/{1}/result/?start={2}&stop={3}' \
                    .format(atlas_uri, id, int(datetime) - 300, datetime)
        results = requests.get(url=uri).json()

        return results

    def _get_latest_data(self, id):
        """
        get the latest measurement data
        :param id measurement id
        :return:
        """
        uri = '{0}measurement-latest/{1}/'.format(atlas_uri, id)
        results = requests.get(url=uri).json()

        return results

    def _get_asn(self, prefix):
        """
        query db to get ASN of a certain prefix from database
        :param prefix:
        :return:
        """
        # TODO: should support IPv6 ASN
        query = {'prefix': prefix}
        result = self.db.prefix_asn_mapping.find_one(query)
        if result is None:
            return '0'

        return result['asn']

    def _get_probes_in_asn(self, asn):
        """
        get all probes in a certain ASN from database
        :return:
        """
        query = {'asn4': int(asn)}
        query_result = self.db.probes.find(query)
        result = []
        for res in query_result:
            result.append(res['prb_id'])

        return result

    def _get_probes_v6_in_asn(self, asn):
        """
        get all probes in a certain ASN from database
        :return:
        """
        query = {'asn6': int(asn)}
        query_result = self.db.probes.find(query)
        result = []
        for res in query_result:
            result.append(res['prb_id'])

        return result

    def traceroute_data(self, datetime):
        """
        process traceroute data (ipv4 or ipv6) retrieved from RIPE Atlas
        :param datetime end time
        :return:
        """
        traceroute_data = list()
        if self.ip_version is Version.ipv4:
            traceroute_data = self._get_data(data_type=RipeAtlasData.traceroute, id=msmnt_id, datetime=datetime)
        if self.ip_version is Version.ipv6:
            traceroute_data = self._get_data(data_type=RipeAtlasData.traceroute, id=msmnt_id6, datetime=datetime)

        result = []

        # TODO: add exception handler if traceroute_data is empty
        for index, msmnt in enumerate(traceroute_data):
            path = []
            for result_per_probe in msmnt['result']:
                if 'from' in result_per_probe['result'][0]:  # at the moment, take care only the first result of traceroute
                    hop = result_per_probe['result'][0]['from']
                    hop_prefix = None
                    hop_prefix_str = None

                    if self.ip_version is Version.ipv4:
                        hop_prefix = ipaddress.ip_interface(hop + '/24')
                        hop_prefix_str = str(hop_prefix.network).split('/24')[0]

                    if self.ip_version is Version.ipv6:
                        hop_prefix = ipaddress.ip_interface(hop + '/48')
                        hop_prefix_str = str(hop_prefix.network).split('/48')[0]

                    # if the prefix is a public address and its ASN is not 0
                    if not hop_prefix.is_private:
                        if self.ip_version is Version.ipv4:
                            asn = self._get_asn(hop_prefix_str)  # this line queries from db
                        if self.ip_version is Version.ipv6:
                            try:
                                # TODO: should use bulk query
                                asn = cymru.get_asn(hop_prefix_str)['asn']  # this line queries from cymru
                            except:
                                print('error encountered for: {}'.format(hop_prefix_str))
                        if asn is not '0':
                            path.append(asn)
            path.append(peering_asn)  # for the sake of the tree
            path.append(" ")  # for the sake of the tree
            result.append({})
            result[index]['prb_id'] = str(msmnt['prb_id'])
            result[index]['path'] = path

        # return final result
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

        result = Encoder().encode(root_list)[1:-1]
        print(result)
        return result
