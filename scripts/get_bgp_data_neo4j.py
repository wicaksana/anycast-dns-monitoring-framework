import requests
import pytz
import time
import string
from py2neo import Graph
from datetime import datetime
from scripts.params import root_prefix, root_prefix6

"""
- It populates Neo4j
- The processed data is primarily used for visualization, therefore:
- It downloads *all* Root Servers' BGP RIB data, and from 2001 to 2016, way more than what I use in my Thesis
- It uses *all* peers that provides reachability to a certain prefix type (IPv4 or IPv6), in contrast to get_bgp_data_mongodb.py
"""

base_url = 'https://stat.ripe.net/data/bgp-state/data.json?'
graph = Graph(password='neo4jneo4j')


def get_data(prefix, timestamp):
    """
    Download data from RIPE RIS and store it at Neo4j
    get data for each Root Server
    :param prefix: well, actually the Root Server's IP address, not prefix
    :param timestamp: timestamp
    :return:
    """
    url = '{0}resource={1}&timestamp={2}'.format(base_url, prefix, timestamp)
    print('url: {}'.format(url))
    data = requests.get(url).json()

    bgp_data = data['data']['bgp_state']

    if bgp_data:
        for route_info in bgp_data:
            as_path = route_info['path']
            as_path.reverse()  # too lazy to change the code below, so simply do .reverse()

            cur_node = None
            prev_node = None

            counter_as_prepend = 0
            for index, asn in enumerate(as_path):
                cur_node = asn
                graph.run('MERGE(s:asn{{name:"{0}", label:"{0}"}})'.format(asn))  # create new node if not exist.
                if index > 0:
                    if cur_node != prev_node:
                        query = 'MATCH (s:asn),(d:asn) ' \
                                'WHERE s.name="{0}" AND d.name="{1}" ' \
                                'MERGE (s)-[r:TO {{prefix: "{3}", time: {2}, prepended: {4}}}]->(d)' \
                            .format(cur_node, prev_node, timestamp, prefix, counter_as_prepend)
                        graph.run(query)
                        if counter_as_prepend > 0:
                            counter_as_prepend = 0  # reset
                    else:  # AS prepending
                        counter_as_prepend += 1
                prev_node = cur_node
    else:
        print('bgp_data empty for prefix {0} timestamp {1}'.format(prefix, timestamp))


def main():
    utc = pytz.utc
    for year in range(2001, 2016):
        print('year: {}'.format(year))
        for month in range(1, 13):
            dt = datetime(year, month, 1, 1, 0, 0)  # I use 1:00 AM because my local time is UTC+1. Adjust it to your TZ
            utc_dt = utc.localize(dt)
            timestamp = int(time.mktime(utc_dt.timetuple()))

            root_list = string.ascii_lowercase[:13] # A to M-Root

            for root_server4 in root_list:
                prefix = root_prefix(root_server4, timestamp)
                if prefix:
                    get_data(prefix, timestamp)

            for root_server6 in root_list:
                prefix = root_prefix6(root_server6, timestamp)
                if prefix:
                    get_data(prefix, timestamp)


if __name__ == '__main__':
    main()