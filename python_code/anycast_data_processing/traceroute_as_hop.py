import sys
import os
import json
import ipaddress
from pprint import pprint
from .node import Node
from .encoder import Encoder

DATASET = '../datasets/'
PROBE_AS_LIST = DATASET + 'prb_as'
PROBE_LIST = DATASET + 'prb_id_list'
PREFIX_AS_LIST = DATASET + 'block_to_as_summary'
RIPE_ATLAS_JSON = DATASET + '20160101.json'


def get_probe_as(probe_as_list):
    """
    load the probe-ASN map by reading prb_as
    :param probe_as_list: probe-ASN map file
    :return: map of probe-ASN in dictionary format
    """
    probe_as = {}
    if os.path.exists(probe_as_list):
        with open(probe_as_list, 'r') as input_file:
            for line in input_file:
                probe_as[line.split(' ')[0]] = line.split(' ')[1].strip()
    else:
        print("[!] File {} not found!".format(probe_as_list))
    return probe_as


def get_prefix_to_as(prefix_as_list):
    """
    load the prefix-ASN map from block_to_as_summary
    :param prefix_as_list: IP prefix-ASN map file
    :return: map of prefix-ASN in dictionary format
    """
    prefix_as = {}
    if os.path.exists(prefix_as_list):
        with open(prefix_as_list, 'r') as input_file:
            for line in input_file:
                splitted_line = line.split(' ')
                if splitted_line[1] == 'NA\n':
                    prefix_as[splitted_line[0]] = 0
                else:
                    prefix_as[splitted_line[0]] = int(splitted_line[1])
    else:
        print("[!] File {} not found!".format(prefix_as_list))
    return prefix_as


def get_probe_list(probe_list):
    """
    load the probe list
    :param probe_list:
    :return: non-duplicate set of the probes
    """
    probes = set()
    if os.path.exists(probe_list):
        with open(probe_list, 'r') as input_file:
            for probe in input_file:
                probes.add(probe.strip())
    else:
        print("[!] File {} not found!".format(probe_list))
    return probes


def get_traceroute_data(ripe_atlas_json):
    """
    parse traceroute measurements
    :param ripe_atlas_json: JSON from RIPE Atlas
    :return:
    """
    traceroute_result = {}
    if os.path.exists(ripe_atlas_json):
        with open(ripe_atlas_json, 'r') as input_file:
            data = json.load(input_file)

        for measurement in data:
            if 'result' in measurement:
                prb_id = measurement['prb_id']
                if prb_id not in traceroute_result:
                    traceroute_result[prb_id] = []
                traceroute_result[prb_id].append([])

                for hop in measurement['result']:
                    if 'from' in hop['result'][0]:
                        traceroute_result[prb_id][len(traceroute_result[prb_id]) - 1].append(hop['result'][0]['from'])
    else:
        print("[!] File {} not found!".format(ripe_atlas_json))
    return traceroute_result


def get_asn_path(peering_asn, probe_list, prefix_as, traceroute_data):
    """
    translate traceroute path into ASN path
    :param peering_asn:
    :param probe_list:
    :param prefix_as:
    :param traceroute_data:
    :return: map of probe ID to its ASN path
    """
    probes_asn_path_list = {}

    for probe in probe_list:
        probes_asn_path_list[probe] = []
        # use the longest traceroute path
        for hop in max(traceroute_data[int(probe)]):
            ip_prefix = ipaddress.ip_interface(hop + '/24').network
            ip_prefix_str = str(ip_prefix).split('/24')[0]

            # if the prefix is a public address and contained in the prefix-ASN map
            if not ip_prefix.is_private and ip_prefix_str in prefix_as:
                if prefix_as[ip_prefix_str] != 0 and prefix_as[ip_prefix_str] not in probes_asn_path_list:
                    probes_asn_path_list[probe].append(prefix_as[ip_prefix_str])

        probes_asn_path_list[probe].append(int(peering_asn))
        probes_asn_path_list[probe].append(' ')

    return probes_asn_path_list


def main():
    peering_asn = '47065'  # default

    if len(sys.argv) < 2:
        print("[!] put the PEERING ASN as the argument")
        sys.exit(1)
    else:
        peering_asn = str(sys.argv[1])

    probe_as = get_probe_as(PROBE_AS_LIST)
    prefix_as = get_prefix_to_as(PREFIX_AS_LIST)
    probe_list = get_probe_list(PROBE_LIST)
    traceroute_data = get_traceroute_data(RIPE_ATLAS_JSON)
    probes_asn_path_list = get_asn_path(peering_asn, probe_list, prefix_as, traceroute_data) # equivalent to hop_list_list

    rootlist = []

    # temp ###############
    # print("\n\n[!] probe list from probe_list: \n{} ".format(sorted(probe_list)))
    # print("\n\n[!] probe list from probes_asn_path_list: \n{}\n\n".format(sorted(probes_asn_path_list)))
    # print("\n\n")
    # print("[!] probe_list length: {}".format(len(probe_list)))
    # print("[!] probes_asn_path_list length: {}".format(len(probes_asn_path_list)))
    # for i in probe_list:
    #     if i not in probes_asn_path_list:
    #         print("[!] probe {} not in probes_asn_path_list!".format(i))
    # print("\n\n")
    # temp ###############

    # pprint(probes_asn_path_list)
    # print()

    # create the tree. Simply copy it from hackathon code
    for probe_id in probes_asn_path_list:
        as_path = probes_asn_path_list[probe_id]
        as_path.reverse()

        # print("probe: {} ==> AS path: {}".format(probe_id, as_path))
        level = 0
        cur_node = None

        for asn in as_path:
            if level == 0:
                node = None
                matching_nodes = [x for x in rootlist if x.name == str(asn)]
                if len(matching_nodes) > 0:
                    node = matching_nodes[0]
                # the following is only applied during the first time of root node creation
                if node is None:
                    node = Node(str(asn))
                    # node.probes.append(probe_id)
                    rootlist.append(node)
                    # print("[0] node {} is appended to rootlist.".format(node.name))
                cur_node = node
            else:
                node = Node(str(asn))
                if level == len(as_path) - 1: # probe resides in the last element (ASN) of as_path
                    # node.probes.append(probe_id)
                    cur_node = cur_node.add_child(node, probe_id) # probe_id is totally wrong. It should use list of probes in a certain ASN
                else:
                    cur_node = cur_node.add_child(node)

            level += 1
            # print("rootlist: {}, length {}\n".format(rootlist, len(rootlist)))

    # print("var astree = " + Encoder().encode(rootlist)[1:-1] + ";")
    json_data = json.loads(Encoder().encode(rootlist)[1:-1])
    pprint(json_data)


if __name__ == '__main__':
    main()
