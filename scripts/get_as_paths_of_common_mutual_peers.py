import csv
import requests
import pytz
import time
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from scripts.params import root_prefix, root_prefix6

# objective:
# 1. get common mutual peers of a certain Root Servers
# 2. create CSV containing AS path of common mutual peers over certain amount of time

start = datetime(2011, 2, 1, 1, 0, 0)
stop = datetime(datetime.today().year, datetime.today().month, 1, 1, 0, 0)

root_list = 'cm'


def initiate_db():
    client = MongoClient()
    db = client.anycast_monitoring

    cols = db.collection_names()

    for root in root_list:
        if 'evolution_{}_ipv4'.format(root) in cols:
            print('evolution_{}_ipv4 dropped..'.format(root))
            db.drop_collection('evolution_{}_ipv4'.format(root))

        db.create_collection('evolution_{}_ipv4'.format(root))
        db['evolution_{}_ipv4'.format(root)].create_index([
            ('timestamp', ASCENDING),
            ('peer', ASCENDING)
        ])

    return db


def deduplicate(items):
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


def get_peers(prefix, timestamp):
    url = 'https://stat.ripe.net/data/bgp-state/data.json?resource={0}&timestamp={1}'.format(prefix, timestamp)
    print('get_peers {}'.format(url))
    data = requests.get(url).json()
    data = data['data']['bgp_state']

    bgp_data = {}
    peers = []
    if data:
        for item in data:
            bgp_data[item['path'][0]] = list(deduplicate(item['path']))
            peers.append(item['path'][0])
    return bgp_data, peers


def main():
    db = initiate_db()

    utc = pytz.utc
    cur_date = start

    temp = []
    path4 = {}
    path6 = {}

    print('start..')
    for root in root_list:
        print('working on {}-Root..'.format(root))
        while cur_date <= stop:
            #     print(cur_date)
            utc_dt = utc.localize(cur_date)
            timestamp = int(time.mktime(utc_dt.timetuple()))

            prefix4 = root_prefix(root, timestamp)
            prefix6 = root_prefix(root, timestamp)

            data4, peer4 = get_peers(prefix4, timestamp)
            data6, peer6 = get_peers(prefix6, timestamp)

            mutual_peers = set(peer4) & set(peer6)
            temp.append(mutual_peers)
            path4[timestamp] = data4
            path6[timestamp] = data6

            year = cur_date.year + 1 if cur_date.month == 12 else cur_date.year
            month = 2 if cur_date.month == 12 else cur_date.month + 2  # increment for each two months
            cur_date = datetime(year, month, 1, 1, 0, 0)

        common_mutual_peers = list(set.intersection(*temp))

        result4 = []
        for ts4 in path4:
            for asn in common_mutual_peers:
                result4.append({
                    'timestamp': ts4,
                    'peer': asn,
                    'path': path4[ts4][asn]
                })
        db['evolution_{}_ipv4'.format(root)].insert_many(result4)

        result6 = []
        for ts6 in path6:
            for asn in common_mutual_peers:
                result6.append({
                    'timestamp': ts6,
                    'peer': asn,
                    'path': path6[ts6][asn]
                })
        db['evolution_{}_ipv6'.format(root)].insert_many(result6)

    print('finish.')


if __name__ == '__main__':
    main()