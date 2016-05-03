import sys
import os
import json
from pprint import pprint
from .node import Node
from .encoder import Encoder
from .traceroute_as_hop import PROBE_LIST, PROBE_AS_LIST, get_probe_list

"""
used to generate control-plane data
desired input:
- as-path-reverse-amster
- as-path-reverse-noamster
WARNING. those two files about should provide information about the probe IDs located in the ASN as well.
"""


def get_probes_id(asn):
    """
    get the list of probe IDs in a certain ASN
    :param asn:
    :return: list of probe IDs
    """
    probe_list = get_probe_list(PROBE_LIST)
    probe_as = {}
    if os.path.exists(PROBE_AS_LIST):
        with open(PROBE_AS_LIST, 'r') as input_file:
            for line in input_file:
                probe_as[line.split(' ')[0]] = line.split(' ')[1].strip()
    else:
        print("[!] File {} not found!".format(PROBE_AS_LIST))
        return []

    probes = []
    for key in probe_as:
        # if probe_as[key] == asn and key in probe_list:  # WARNING, the following line does not check whether the probe is present in the probe_List
        if probe_as[key] == asn:
            probes.append(key)
    return probes


def main():
    file_path = sys.argv[1]
    hop_list_list = []

    with open(file_path, 'r') as input_file:
        for line in input_file:
            hop_list = list()
            hop_list.append(" ")
            as_list = line.split(' ')
            for hop in as_list:
                hop_list.append(hop.strip())

            if len(hop_list) > 1:
                hop_list_list.append(hop_list)

    root_list = []
    for as_list in hop_list_list:
        level = 0
        cur_node = None

        for asn in as_list:
            if level == 0:
                node = None
                matching_nodes = [x for x in root_list if x.name == str(asn)]
                if len(matching_nodes) > 0:
                    node = matching_nodes[0]
                if node is None:
                    node = Node(str(asn))
                    root_list.append(node)
                cur_node = node
            else:
                node = Node(str(asn))
                if level == len(as_list) - 1: # probe resides in the last element (ASN) of as_path
                    # node.probes.append(probe_id)
                    cur_node = cur_node.add_child(node, get_probes_id(asn))
                else:
                    cur_node = cur_node.add_child(node)
            level += 1

    # print(Encoder().encode(root_list)[1:-1])
    json_data = json.loads(Encoder().encode(root_list)[1:-1])
    pprint(json_data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("you need the input file (")
        sys.exit(1)

    main()
