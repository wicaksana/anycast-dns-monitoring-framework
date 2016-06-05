import sys
import requests
from requests.exceptions import SSLError
from _pybgpstream import BGPRecord, BGPStream
from pymongo import MongoClient
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.node import Node
from anycast_dns_monitoring.data_processing.encoder import Encoder


class Ris:
    """
    get control-plane data from RIS. For the latest data, use the REST service directly since it is much faster.
    For historical data, use BGPStream
    """
    def __init__(self, ip_version):
        self.db = self._initiate_db()
        self.ip_version = ip_version
        print('[*] ris.py: Ris object initiated, using {}'.format(self.ip_version))

    def _initiate_db(self):
        """
        initiate connection to mongodb
        :return: database instance
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

    def _get_data(self, prefix, datetime):
        """
        output example: [['15547', '8220', '1853', '1205'],[..another AS path..]]
        :param prefix:
        :param datetime: end interval
        :return: list of AS paths
        """
        print('[*] ris.py: _get_data() called')
        print('[*] ris.py: _get_data() prefix: {}'.format(prefix))
        start = int(datetime) - 20000  # 20000 second seems to be the shortest interval to get data from BGPstream
        stop = int(datetime)
        result = []

        stream = BGPStream()
        rec = BGPRecord()

        stream.add_filter('prefix', prefix)
        stream.add_filter('record-type', 'ribs')
        stream.add_filter('project', 'ris')
        stream.add_interval_filter(start, stop)

        stream.start()

        while stream.get_next_record(rec):
            if rec.status == "valid":
                elem = rec.get_next_elem()
                while elem:
                    as_path = elem.fields['as-path'].split()
                    as_path.append(' ')  # for tree creation
                    result.append(as_path)
                    elem = rec.get_next_elem()
        print('[*] ris.py: _get_data() finished.')
        return result

    def _get_latest_data(self, prefix):
        """
        to get the latest data, use data directly from RIS to speed things up
        :return:
        """
        uri = '{0}looking-glass/data.json?resource={1}'.format(params.ris_uri, prefix)
        result = []
        try:
            data = requests.get(uri, verify=False).json()['data']
            for rrc in data['rrcs']:
                for peer in data['rrcs'][rrc]['entries']:
                    # path = peer['as_path'].strip().split(' ')
                    path = peer['as_path'].strip().split(',')[0].split(
                        ' ')  # split by comma is to anticipate aggregration info
                    path.append(' ')  # for the sake of tree creation code
                    result.append(path)
        except SSLError as e:
            print('[!] Get error: {}'.format(e))

        return result

    def tree_control_plane(self, datetime=None):
        """
        send data for control-plane tree visualization
        :param datetime
        :return:
        """
        print('[*] ris.py: datetime: {}'.format(datetime))

        if datetime is None and self.ip_version is params.Version.ipv4:
            print('[*] ris.py: call self._get_latest_data(params.prefix) ')
            data = self._get_latest_data(params.prefix)  # get the latest IPv4 control-plane data

        elif datetime is None and self.ip_version is params.Version.ipv6:
            print('[*] ris.py: call self._get_latest_data(params.prefix6) ')
            data = self._get_latest_data(params.prefix6)  # get the latest IPv6 control-plane data

        elif datetime is not None and self.ip_version is params.Version.ipv4:
            print('[*] ris.py: call self._get_data(params.prefix, datetime) ')
            data = self._get_data(params.prefix, datetime)  # get IPv4 control-plane data

        elif datetime is not None and self.ip_version is params.Version.ipv6:
            print('[*] ris.py: call self._get_data(params.prefix6, datetime) ')
            data = self._get_data(params.prefix6, datetime)  # get IPv6 control-plane data

        else:
            print('something wrong with the input variables of tree_control_plane()!')
            sys.exit(1)

        print('[*] ris.py: data: {}'.format(data))

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
        print('control-plane tree: {}'.format(result))
        return result
