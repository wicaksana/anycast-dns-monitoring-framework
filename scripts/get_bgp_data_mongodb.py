import requests
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from scripts.params import root_prefix, root_prefix6
from datetime import datetime
import pytz
import time

"""
- It populates MongoDB
- The processed data is primarily used for analysis, therefore
- In contrast to get_bgp_data_neo4j.py, this script *only* takes into account mutual peers (must have both IPv4 and IPv6 reachability
  information)
"""

root_list = 'acdfijklm'
start = datetime(2008, 3, 1, 1, 0, 0)
stop = datetime(2008, 5, 1, 1, 0, 0)


def db_init():
    """
    http://stackoverflow.com/a/19278887/5658688
    since BGP doesn't allow path loop, recurring ASN only happens in AS prepending case
    initiate the database
    :return:
    """
    client = MongoClient()
    db = client.anycast_monitoring

    cols = db.collection_names()

    for r in root_list:
        if '{}_root'.format(r) in cols:
            print('{}_root dropped..'.format(r))
            db.drop_collection('{}_root'.format(r))

        db.create_collection('{}_root'.format(r))
        db['{}_root'.format(r)].create_index([
            ('timestamp', ASCENDING),
            ('peer', ASCENDING)
        ])
        print('{}_root re-created..'.format(r))

    return db


def deduplicate(items):
    """
    remove duplicate items
    :param items:
    :return:
    """
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


def get_peers(prefix, timestamp):
    """
    Get BGP data from RIPEStat
    :param prefix:
    :param timestamp:
    :return: bgp_data (path, collector), peer list
    """
    url = 'https://stat.ripe.net/data/bgp-state/data.json?resource={0}&timestamp={1}'.format(prefix, timestamp)
    print(url)
    data = requests.get(url).json()
    data = data['data']['bgp_state']

    bgp_data = {}
    peers = []
    if data:
        for item in data:
            coll = item['source_id'].split('-')[0]  # collector
            peer = item['path'][0]  # peer ASN
            bgp_data[peer] = {'path': list(deduplicate(item['path'])), 'collector': coll}  # doesn't care about AS prepending
            peers.append(peer)
    return bgp_data, peers


def run(r):
    """
    main execution
    :return:
    """
    print('working on {}-Root..'.format(root))
    container = []  # data container to be stored in db
    utc = pytz.utc
    cur_date = start

    while cur_date <= stop:
        print('\t{0} - {1}'.format(r, cur_date))
        utc_dt = utc.localize(cur_date)
        timestamp = int(time.mktime(utc_dt.timetuple()))

        prefix4 = root_prefix(r, timestamp)
        prefix6 = root_prefix6(r, timestamp)

        data4, peer4 = get_peers(prefix4, timestamp)
        data6, peer6 = get_peers(prefix6, timestamp)

        mutual_peers = set(peer4) & set(peer6)  # get mutual peers

        for asn in mutual_peers:
            res = dict()
            res['timestamp'] = timestamp
            res['peer'] = asn
            res['path4'] = data4[asn]['path']
            res['path6'] = data6[asn]['path']
            res['collector'] = data4[asn]['collector']
            container.append(res)

        # increment cur_date
        year = cur_date.year + 1 if cur_date.month == 12 else cur_date.year
        month = 1 if cur_date.month == 12 else cur_date.month + 1
        cur_date = datetime(year, month, 1, 1, 0, 0)

    db['{}_root'.format(root)].insert_many(container)


if __name__ == '__main__':
    db = db_init()
    for root in root_list:
        run(root)
