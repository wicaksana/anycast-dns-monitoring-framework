# -*- coding: utf-8 -*-
from pymongo import MongoClient
import requests

def main():
    client = MongoClient()
    anycast = client.anycast_monitoring
    probes = anycast.probes

    for probe in probes.find():
        try:
            uri = 'https://atlas.ripe.net/api/v1/probe/{}/'.format(probe['prb_id'])
            data = requests.get(uri).json()
            cc = data['country_code']
            probes.update({'prb_id': probe['prb_id']}, {'$set': {'country_code': cc}})
        except:
            print('error: probe {}'.format(probe['prb_id']))

if __name__ == '__main__':
    main()