from pymongo import MongoClient, ASCENDING
from py2neo import Graph
import subprocess
import sys

"""
- Get AS information from Cymru via whois, store it in MongoDB
- It uses unique ASes from Neo4j because Neo4j store data of all peers (not just the mutual ones)
"""
COL_NAME = 'as_info'
INPUT_FILE = 'whois_input.txt'
OUTPUT_FILE = 'whois_output.txt'


def db_init():
    """
    initiate db
    :return: db object
    """
    client = MongoClient()
    db = client.anycast_monitoring

    collections = db.collection_names()

    if COL_NAME in collections:
        print('drop collection "{}"..'.format(COL_NAME))
        db.drop_collection(COL_NAME)

    db.create_collection(COL_NAME)
    db[COL_NAME].create_index([
        ('asn', ASCENDING)
    ])
    print('collection "{}" is created..'.format(COL_NAME))

    return db


def main():
    unique_as = list()  # AS container
    results = graph.run('MATCH (n:asn) RETURN DISTINCT n.name AS name')

    for result in results:
        unique_as.append(result['name'])

    # write input file for bulk whois operation
    with open(INPUT_FILE, 'w') as f:
        f.write('begin\n')
        for item in unique_as:
            f.write('as{}\n'.format(item))
        f.write('end\n')

    # bulk query to Cymru's whois
    # cmd = 'netcat whois.cymru.com 43 < {} | sort -n > {}'.format(INPUT_FILE, OUTPUT_FILE)
    cmd = 'netcat whois.cymru.com 43 < {}'.format(INPUT_FILE)
    p = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    # if we get whois error...
    if err != b'':
        print('There is error in whois query: {}'.format(err))
        sys.exit(1)

    # check output
    clean_out = out.decode('utf-8').strip()
    # print(clean_out)
    out_list = clean_out.split('\n')
    out_list.pop(0)  # remove the first line 'Bulk mode; whois.cymru.com'

    # write to db
    as_info = db['as_info']
    for asn, info in zip(unique_as, out_list):
        if not info:  # if Cymru returns nothing..
            info = '<no information>'
        as_info.insert_one({
            'asn': int(asn),
            'info': info
        })

    print('done.')

if __name__ == '__main__':
    db = db_init()
    graph = Graph(password='neo4jneo4j')
    main()