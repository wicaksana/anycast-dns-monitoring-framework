import os
import time
from geopy.geocoders import OpenCage
import pymongo
import requests
from pymongo import MongoClient
from anycast_dns_monitoring.data_processing import params

cc = ['NL', 'GB', 'FR', 'CH', 'AT', 'JP', 'SE', 'US', 'IT', 'DE', 'RU', 'BR', 'AU', 'KE', 'SG', 'ZA', 'RS']

def initiate_db():
    client = MongoClient()
    db = client.anycast_monitoring

    cols = db.collection_names()
    if 'probes' in cols:
        print('dropping collection \'probes\'..')
        db.drop_collection('probes')
    if 'prefix_asn_mapping' in cols:
        print('dropping collection \'prefix_asn_mapping\'..')
        db.drop_collection('prefix_asn_mapping')

    db.create_collection('probes')
    db.create_collection('prefix_asn_mapping')
    db.prefix_asn_mapping.create_index([('prefix', pymongo.ASCENDING)])

    return db


def get_ip_asn_of_probe(prb_id):
    """
    get IP addresses and ASNs of a certain probe
    :param prb_id:
    :return: array of dictionaries containing probe ID, IPv4, IPv6, ASNv4, ASNv6
    """
    uri = 'https://atlas.ripe.net/api/v1/probe/{}/'.format(prb_id)
    result = requests.get(url=uri).json()

    return result['address_v4'], result['address_v6'], result['asn_v4'], result['asn_v6']


# def get_address(lat, lon):
#     """
#     get address of probe
#     :param lat: lattitude
#     :param lon: longitude
#     :return: the address. Returns None if lat and lon are None
#     """
#     if lat is not None and lon is not None:
#         geolocator = OpenCage()
#         return geolocator.reverse('{}, {}'.format(lat, lon)).address
#     else:
#         return None


def get_all_probes():
    """
    get all probes of RIPE Atlas
    :return:
    """
    uri = 'https://atlas.ripe.net/api/v1/probe/?limit=100'
    next_uri = ''
    result = []

    while next_uri is not None:
        data = requests.get(uri).json()
        next_uri = data['meta']['next']
        print(uri)

        for probe in data['objects']:
            if probe['status'] == 1 and probe['country_code'] in cc:  # if the probe is connected
                result.append({'prb_id': probe['id'],
                    'ipv4': probe['address_v4'],
                    'ipv6': probe['address_v6'],
                    'asn4': probe['asn_v4'],
                    'asn6': probe['asn_v6'],
                    'latitude': probe['latitude'],
                    'longitude': probe['longitude'],
                    # 'address': get_address(probe['latitude'], probe['longitude']) # do it later
                })

        if next_uri is not None:
            uri = 'https://atlas.ripe.net' + next_uri
    print(len(result))
    return result


def get_probe_list(measurement_id):
    """
    get list of probes used in a certain measurement
    :param measurement_id:
    :return: array of probe IDs used
    """
    uri = 'https://atlas.ripe.net/api/v1/measurement/{}/?fields=probes'.format(measurement_id)
    probes_list = requests.get(url=uri).json()
    result = []
    if probes_list['probes']:
        for index, probe in enumerate(probes_list['probes']):
            result.append({})
            ipv4, ipv6, asn4, asn6 = get_ip_asn_of_probe(probe['id'])
            result[index]['prb_id'] = probe['id']
            result[index]['ipv4'] = ipv4
            result[index]['ipv6'] = ipv6
            result[index]['asn4'] = asn4
            result[index]['asn6'] = asn6
    else:  # empty probe, which means it uses all probes
        print('the measurement ID does not contain any probe list. Get all probes instead...')
        result = get_all_probes()
    return result


def populate_probes(prb_list, used_db):
    print('populating \'probes\'..')
    for probe in prb_list:
        used_db.probes.insert(probe)
    # used_db.probes.insert_many(prb_list)
    print('done.')


def query_probes(queried_db):
    queried_probes = queried_db.probes.find_one()
    print(queried_probes)


def query_maps(queried_db):
    queried_map = queried_db.prefix_asn_mapping.find_one()
    print(queried_map)

if __name__ == '__main__':
    db = initiate_db()
    probe_list = get_probe_list(params.traceroute_id)
    # list of countries where route collectors of RIS and RouteViews reside

    # populate probe list
    populate_probes(prb_list=probe_list, used_db=db)

    # populate prefix->ASN map
    prefix_asn_map = '../anycast_dns_monitoring/static/datasets/block_to_as_summary'
    map = []
    if os.path.exists(prefix_asn_map):
        with open(prefix_asn_map, 'r') as input_file:
            print('read block_to_as_summary..')
            for line in input_file:
                line_splitted = line.split(' ')
                doc = {}
                doc['prefix'] = line_splitted[0]
                if line_splitted[1] == 'NA\n':
                    doc['asn'] = '0'
                else:
                    doc['asn'] = line_splitted[1].strip()  # mongodb does not allow . in keys
                map.append(doc)
    else:
        print("[!] File {} not found!".format(prefix_asn_map))

    print('finish reading file. perform bulk insert..')
    db.prefix_asn_mapping.insert_many(map)

    query_maps(queried_db=db)
    query_probes(queried_db=db)

    print('* Finish *')