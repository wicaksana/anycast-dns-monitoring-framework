from _pybgpstream import BGPStream, BGPElem, BGPRecord
from py2neo import Graph, Node, Relationship
from datetime import datetime
import pytz
import time


def get_data(timestamp):
    graph = Graph(password="neo4jneo4j")

    stream = BGPStream()
    rec = BGPRecord()
    rec_time = None

    stream.add_filter('prefix', '198.41.0.0/24')  # A-root
    stream.add_filter('prefix', '192.33.4.0/24')  # C-root
    stream.add_filter('prefix', '199.7.91.0/24')  # D-root
    stream.add_filter('prefix', '192.203.230.0/24')  # E-root, IPv4 only
    stream.add_filter('prefix', '192.5.5.0/24')  # F-root
    stream.add_filter('prefix', '192.112.36.0/24')  # G-root, IPv4 only
    stream.add_filter('prefix', '198.97.190.0/24')  # H-root
    stream.add_filter('prefix', '192.36.148.0/24')  # I-root
    stream.add_filter('prefix', '192.58.128.0/24')  # J-root
    stream.add_filter('prefix', '193.0.14.0/24')  # K-root
    stream.add_filter('prefix', '199.7.83.0/24')  # L-root
    stream.add_filter('prefix', '202.12.27.0/24')  # M-root

    # IPv6
    stream.add_filter('prefix', '2001:503:ba3e::/48')  # A
    stream.add_filter('prefix', '2001:500:2::/48')  # C
    stream.add_filter('prefix', '2001:500:2d::/48')  # D
    stream.add_filter('prefix', '2001:500:2f::/48')  # F
    stream.add_filter('prefix', '2001:500:1::/48')  # H
    stream.add_filter('prefix', '2001:7fe::/33')  # I
    stream.add_filter('prefix', '2001:503:c27::/48')  # J
    stream.add_filter('prefix', '2001:7fd::/48')  # K
    stream.add_filter('prefix', '2001:500:9f::/48')  # L
    stream.add_filter('prefix', '2001:dc3::/32')  # M

    stream.add_filter('record-type', 'ribs')
    # stream.add_filter('collector', 'route-views.soxrs')
    stream.add_filter('project', 'routeviews')
    stream.add_interval_filter(timestamp, timestamp)

    stream.start()

    result = {}
    while stream.get_next_record(rec):
        rec_time = rec.time
        if rec.status == "valid":
            elem = rec.get_next_elem()
            while elem:
                print rec.collector, elem.type, elem.peer_address, elem.peer_asn, elem.fields
                as_path = elem.fields['as-path'].split()
                as_path.reverse()
                prefix = elem.fields['prefix']
                if prefix not in result:
                    result[prefix] = []
                result[prefix].append(as_path)
                elem = rec.get_next_elem()

    # get only unique lists in result
    for prefix in result:
        result[prefix] = [list(x) for x in set(tuple(x) for x in result[prefix])]
    print('timestamp {} ==> result: {}'.format(rec_time, result))

    for prefix in result:
        for path in result[prefix]:
            print('path: {}'.format(path))
            cur_node = None
            prev_node = None
            counter_as_prepend = 0
            for index, asn in enumerate(path):
                cur_node = asn
                searched_node = graph.run('match(n:asn) where n.name="{0}" return n'.format(asn))
                if not searched_node.forward():  # there is already existing node
                    graph.create(Node('asn', name=str(asn), label=str(asn)))
                if index > 0:
                    if cur_node != prev_node:
                        query = 'MATCH (s:asn),(d:asn) ' \
                                'WHERE s.name="{0}" AND d.name="{1}" ' \
                                'CREATE (s)-[r:TO {{prefix: "{3}", time: {2}, prepended: {4}}}]->(d)'\
                            .format(cur_node, prev_node, rec_time, prefix, counter_as_prepend)
                        graph.run(query)
                        if counter_as_prepend > 0:
                            counter_as_prepend = 0  # reset
                    else:  # AS prepending
                        counter_as_prepend += 1
                prev_node = cur_node


def main():
    utc = pytz.utc
    for month in range(1, 3):
        dt = datetime(2015, month, 1, 1, 0, 0)
        utc_dt = utc.localize(dt)
        timestamp = int(time.mktime(utc_dt.timetuple()))

        get_data(timestamp)


if __name__ == '__main__':
    main()