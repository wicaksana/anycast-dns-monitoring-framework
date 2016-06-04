import requests
import ipaddress
import time
from anycast_dns_monitoring.data_processing.node import Node
from anycast_dns_monitoring.data_processing.encoder import Encoder
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.params import RipeAtlasData, Version
from anycast_dns_monitoring.data_processing.params import atlas_uri, traceroute_id, traceroute6_id, root_asn
import anycast_dns_monitoring.data_processing.cymru as cymru
from anycast_dns_monitoring.data_processing.db import Db


class RipeAtlas:
    """
    anything related to RIPE Atlas
    currently, data related to probes are pre-populated. It should be updated daily, or if there is any changes, this
    should support immediate update (add method to do that)
    """
    def __init__(self, ip_version):
        self.db = Db()
        self.ip_version = ip_version
        print('RipeAtlas object initiated, using {}'.format(self.ip_version))

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
                    .format(atlas_uri, id, int(datetime) - 1800, datetime)
            else:
                uri = '{0}measurement/{1}/result/?start={2}&stop={3}' \
                    .format(atlas_uri, id, int(datetime) - 1800, datetime)
                print('_get_data() ipv6 uri: {}'.format(uri))
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
        if self.ip_version is Version.ipv4:
            query = {'prefix': prefix}
            result = self.db.find_one(params.map4, query=query)
        else:
            query = {'ip': prefix}
            result = self.db.find_one(params.map6, query=query)
        if result is None:
            return '0'

        return result['asn']

    def _get_probes_in_asn(self, asn):
        """
        get all probes in a certain ASN from database
        :return:
        """
        query = {'asn4': int(asn)}
        # query_result = self.db.probes.find(query)
        query_result = self.db.find(col=params.probes, query=query)
        result = []
        for res in query_result:
            result.append(res['prb_id'])

        return result

    def _get_probes6_in_asn(self, asn):
        """
        get all probes in a certain ASN from database
        :return:
        """
        query = {'asn6': int(asn)}
        query_result = self.db.find(col=params.probes, query=query)

        result = []
        for res in query_result:
            result.append(res['prb_id'])
        return result

    def traceroute_data(self, datetime):
        if self.ip_version is Version.ipv4:
            return self._traceroute4_data(datetime)
        else:
            return self._traceroute6_data(datetime)

    def _traceroute4_data(self, datetime):
        """
        process traceroute data (ipv4 or ipv6) retrieved from RIPE Atlas
        :param datetime end time
        :return:
        """
        traceroute_data = self._get_data(data_type=RipeAtlasData.traceroute, id=traceroute_id, datetime=datetime)

        result = []

        # TODO: add exception handler if traceroute_data is empty
        for index, msmnt in enumerate(traceroute_data):
            path = []
            for result_per_probe in msmnt['result']:
                if 'from' in result_per_probe['result'][0]:  # at the moment, take care only the first result of traceroute
                    hop = result_per_probe['result'][0]['from']

                    hop_prefix = ipaddress.ip_interface(hop + '/24')
                    hop_prefix_str = str(hop_prefix.network).split('/24')[0]

                    # if the prefix is a public address and its ASN is not 0
                    if not hop_prefix.is_private:
                        asn = self._get_asn(hop_prefix_str)  # this line queries from db
                        if asn is not '0':
                            path.append(asn)
            path.append(root_asn)  # for the sake of the tree
            path.append(" ")  # for the sake of the tree
            result.append({})
            result[index]['prb_id'] = str(msmnt['prb_id'])
            result[index]['path'] = path

        # return final result
        return result

    def _traceroute6_data(self, datetime):
        """
        process IPv6 traceroute data.
        It is processed differently because it has to use bulk query to cymru
        :param datetime:
        :return:
        """
        traceroute_data = self._get_data(data_type=RipeAtlasData.traceroute, id=traceroute6_id, datetime=datetime)

        # store prefix6-ASN maps to database first
        ip_set = set()
        for msmnt in traceroute_data:
            for res in msmnt['result']:
                if 'result' in res:
                    if 'from' in res['result'][0]:
                        ip_set.add(res['result'][0]['from'])

        # query cymru using bulk data, then store in database
        query_result = cymru.get_bulk_asn(ip_set)
        cymru.write_to_db(self.db, query_result)

        # process traceroute6 data
        result = []

        for index, msmnt in enumerate(traceroute_data):
            path = []
            for result_per_probe in msmnt['result']:
                try:
                    if 'result' in result_per_probe:
                        if 'from' in result_per_probe['result'][0]:  # at the moment, take care only the first result of traceroute
                            hop = result_per_probe['result'][0]['from']
                            hop_prefix = ipaddress.ip_interface(hop + '/64')

                            # if the prefix is a public address and its ASN is not 0 or 'NA'
                            if not hop_prefix.is_private:
                                asn = self._get_asn(hop)
                            if asn is not '0' and asn != 'NA':
                                path.append(asn)
                except KeyError:
                    print('result_per_probe: {}'.format(result_per_probe))

            path.append(root_asn)  # for the sake of the tree
            path.append(" ")  # for the sake of the tree
            result.append({})
            result[index]['prb_id'] = str(msmnt['prb_id'])
            result[index]['path'] = path

        # return final result
        return result

    def tree_data_plane(self, datetime=None):
        """
        get traceroute measurement for a certain time
        :param datetime
        :return:
        """
        if datetime is None:
            datetime = int(time.time())
        else:
            datetime = int(datetime)

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
        print('data-plane result: {}'.format(result))
        return result
