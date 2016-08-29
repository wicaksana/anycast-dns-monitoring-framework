from pymongo import MongoClient
import pytz
import time
import requests
from datetime import datetime
from scripts.params import root_prefix, root_prefix6

client = MongoClient()
anycast = client.anycast_monitoring
peer_data = anycast.peer_data

base_url = 'https://stat.ripe.net/data/ris-peerings/data.json?'


def get_data(prefix, timestamp):
    """

    :param prefix:
    :param timestamp:
    :return:
    """
    url = '{0}resource={1}&query_time={2}'.format(base_url, prefix, timestamp)
    # print('url: {}'.format(url))
    data = requests.get(url).json()

    peerings = data['data']['peerings']

    container = []

    if peerings:
        for collector in peerings:
            probe = collector['probe']
            for peer in collector['peers']:
                if peer['asn'] != 0 and peer['routes']:  # if ASN is not 0 and it has route to the prefix
                    p = {str(peer['asn']): {'collector': probe['name'], 'info': ''}}
                    container.append(p)
    peer_data.insert({
        'timestamp': timestamp,
        'prefix': prefix,
        'peers': container})


def main():
    utc = pytz.utc
    for year in range(2016, 2017):
        print('year: {}'.format(year))
        for month in range(1, 7):
            dt = datetime(year, month, 1, 1, 0, 0)  # I use 1:00 AM because my local time is UTC+1. Adjust it to your TZ
            utc_dt = utc.localize(dt)
            timestamp = int(time.mktime(utc_dt.timetuple()))

            for root_server in root_prefix:
                prefix = root_prefix[root_server]
                if prefix:
                    get_data(prefix, timestamp)

            for root_server in root_prefix6:
                prefix = root_prefix6[root_server]
                if prefix:
                    get_data(prefix, timestamp)


if __name__=='__main__':
    main()