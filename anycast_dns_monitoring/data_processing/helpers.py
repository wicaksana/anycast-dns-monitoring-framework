import requests
import os
import subprocess


def get_probe_list(measurement_id):
    """
    get list of probes used in a certain measurement
    :param measurement_id:
    :return: array of probe IDs used
    """
    uri = 'https://atlas.ripe.net/api/v1/measurement/{}/?fields=probes'.format(measurement_id)
    probes_list = requests.get(url=uri).json()
    result = []
    for index, probe in enumerate(probes_list['probes']):
        result.append({})
        ipv4, ipv6, asn4, asn6 = get_ip_asn_of_probe(probe['id'])
        result[index]['prb_id'] = probe['id']
        result[index]['ipv4'] = ipv4
        result[index]['ipv6'] = ipv6
        result[index]['asn4'] = asn4
        result[index]['asn6'] = asn6

    return result


def get_prefix_to_asn():
    """
    load the prefix-ASN map from block_to_as_summary
    :param prefix_as_list: IP prefix-ASN map file
    :return: dictionary of prefix-ASN in dictionary format
    """
    prefix_as_list = '/home/arif/Github/anycast-dns-monitoring-framework/anycast_dns_monitoring/data_processing/block_to_as_summary'
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


def get_bulk_asn(probe_ip):
    """
    translate bulk of IP list
    see: https://gist.github.com/ttreitlinger/976700
    :param probe_ip: probe id -> IP dictionary
    :return:
    """
    ## TODO: 1. write IP list into input.txt
    input_file = ''

    ## 2. execute netcat
    cmd = 'netcat whois.cymru.com 43 < {}'.format(input_file)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = process.stderr.read()
    print(process)

    ## TODO: 3. parse the result


def get_ip_asn_of_probe(prb_id):
    """
    get IP addresses and ASNs of a certain probe
    :param prb_id:
    :return: array of dictionaries containing probe ID, IPv4, IPv6, ASNv4, ASNv6
    """
    uri = 'https://atlas.ripe.net/api/v1/probe/{}/'.format(prb_id)
    result = requests.get(url=uri).json()

    return result['address_v4'], result['address_v6'], result['asn_v4'], result['asn_v6']
