import ipaddress
from pprint import pprint
from anycast_dns_monitoring.data_processing.node import Node
from anycast_dns_monitoring.data_processing.encoder import Encoder
from anycast_dns_monitoring.data_processing.helpers import get_probe_list
from anycast_dns_monitoring.data_processing.helpers import get_prefix_to_asn


class TracerouteProcessor:
    """
    to process traceroute data from RIPE Atlas.
    Intended to replace traceroute_as_hop.py
    """
    def __init__(self, json_data, msrmnt_id):
        self.json_data = json_data
        self.msmrmnt_id = msrmnt_id
        self.prefix_to_asn = get_prefix_to_asn()

    def get_traceroute_data(self):
        """
        combination of peel_traceroute and get_asn_path (traeroute_as_hop.py)
        :return: dictionary of probe ID -> traceroute ASN path
        """
        result = []

        for index, msmnt in enumerate(self.json_data):
            path = []
            for result_per_probe in msmnt['result']:
                # for result_per_hop in result_per_probe['result']:
                if 'from' in result_per_probe['result'][0]: # at the moment, take care only the first result of traceroute
                    hop = result_per_probe['result'][0]['from']
                    hop_prefix = ipaddress.ip_interface(hop + '/24')
                    hop_prefix_str = str(hop_prefix.network).split('/24')[0]

                    # if the prefix is a public address and contained in the prefix-ASN map
                    if not hop_prefix.is_private and hop_prefix_str in self.prefix_to_asn:
                        if self.prefix_to_asn[hop_prefix_str] != 0 and self.prefix_to_asn[hop_prefix_str]:
                            path.append(str(self.prefix_to_asn[hop_prefix_str]))
            result.append({})
            result[index]['prb_id'] = str(msmnt['prb_id'])
            result[index]['path'] = path

        return result


    def process(self):
        """
        process the measurement data, return d3-tree-ready data
        taken from main() method of traceroute_as_hop.py
        :return:
        """
        probe_ip_asn = get_probe_list(self.msmrmnt_id)  # should get it from the database, instead of directly call the method
        traceroute_data = self.get_traceroute_data()

        root_list = []

        for probe in traceroute_data:
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
                        cur_node = cur_node.add_child(node, probe['prb_id'])
                    else:
                        cur_node = cur_node.add_child(node)
                level += 1

        # pprint("var astree = " + Encoder().encode(root_list)[1:-1] + ";")
        pprint(Encoder().encode(root_list)[1:-1])
