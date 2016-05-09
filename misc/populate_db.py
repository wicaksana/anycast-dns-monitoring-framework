import os
import pymongo
from pymongo import MongoClient
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.helpers import get_probe_list


def initiate_db():
    client = MongoClient()
    db = client.anycast_monitoring

    cols = db.collection_names()
    if 'probes' in cols:
        print('dropping collection \'probes\'..')
        db.probes.drop()
    if 'prefix_asn_mapping' in cols:
        print('dropping collection \'prefix_asn_mapping\'..')
        db.prefix_asn_mapping.drop()

    db.create_collection('probes')
    db.create_collection('prefix_asn_mapping')
    db.prefix_asn_mapping.create_index([('prefix', pymongo.ASCENDING)])

    return db


def populate_probes(prb_list, used_db):
    print('populating \'probes\'..')
    for probe in prb_list:
        used_db.probes.insert(probe)
    print('done.')


def query_probes(queried_db):
    queried_probes = queried_db.probes.find_one()
    print(queried_probes)


def query_maps(queried_db):
    queried_map = queried_db.prefix_asn_mapping.find_one()
    print(queried_map)

if __name__ == '__main__':
    db = initiate_db()
    probe_list = get_probe_list(params.msmnt_id)

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