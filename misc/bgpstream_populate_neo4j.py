from _pybgpstream import BGPStream, BGPElem, BGPRecord
from py2neo import Graph, Node, Relationship

graph = Graph(password="neo4jneo4j")

stream = BGPStream()
rec = BGPRecord()

# stream.add_filter('prefix', '198.41.0.0/24')  # A-root
# stream.add_filter('prefix', '192.33.4.0/24')  # C-root
# stream.add_filter('prefix', '199.7.91.0/24')  # D-root
# stream.add_filter('prefix', '192.203.230.0/24')  # E-root, IPv4 only
# stream.add_filter('prefix', '192.5.5.0/24')  # F-root
# stream.add_filter('prefix', '192.112.36.0/24')  # G-root, IPv4 only
# stream.add_filter('prefix', '198.97.190.0/24')  # H-root
# stream.add_filter('prefix', '192.36.148.0/24')  # I-root
# stream.add_filter('prefix', '192.58.128.0/24')  # J-root
stream.add_filter('prefix', '193.0.14.0/24')  # K-root
stream.add_filter('prefix', '199.7.83.0/24')  # L-root
stream.add_filter('prefix', '202.12.27.0/24')  # M-root

stream.add_filter('record-type','ribs')
# stream.add_filter('collector','route-views.sg')
stream.add_filter('project','routeviews')
timestamp = 1464739200  # 2016/6/1 00:00
stream.add_interval_filter(timestamp, timestamp)  # 1464682200 ==> 05/31/2016 @ 8:10am (UTC); 1464682200

stream.start()

result = {}
while stream.get_next_record(rec):
    if rec.status == "valid":
        elem = rec.get_next_elem()
        while elem:
            print(rec.collector, elem.type, elem.peer_address, elem.peer_asn, elem.fields)
            as_path = elem.fields['as-path'].split()
            as_path.reverse()
            prefix = elem.fields['prefix']
            if prefix not in result:
                result[prefix] = []
            result[prefix].append(as_path)
            elem = rec.get_next_elem()

# get only unique lists in result

# print('res: {}'.format(result))
for prefix in result:
    result[prefix] = [list(x) for x in set(tuple(x) for x in result[prefix])]
print('result: {}'.format(result))

for prefix in result:
    for path in result[prefix]:
        print('path: {}'.format(path))
        cur_node = None
        prev_node = None
        counter_as_prepend = 0
        for index, asn in enumerate(path):
            searched_node = graph.find('asn', property_key='label', property_value=asn)
            try:
                cur_node = searched_node.next()  # see if the AS node is already in the db or not. If yes, cur_node == prev_node
            except StopIteration:
                cur_node = Node('asn', label=str(asn))  # if not exists, then create a new one
            if index > 0:
                if index == len(path) - 1:
                    cur_node['path'] = path  # attach AS path to the last ASN
                if cur_node != prev_node:
                    if counter_as_prepend > 0:
                        cur_node['prepended'] = counter_as_prepend
                        counter_as_prepend = 0  # reset
                    text = 'PEER_{}'.format(prefix)
                    peering = Relationship(cur_node, text, prev_node)
                    peering['time'] = timestamp
                    graph.create(peering)
                else:  # AS prepending
                    counter_as_prepend += 1
            prev_node = cur_node

# for path in result:
#     print('path: {}'.format(path))
#     cur_node = None
#     prev_node = None
#     counter_as_prepend = 0
#     for index, asn in enumerate(path):
#         searched_node = graph.find('asn', property_key='label', property_value=asn)
#         try:
#             cur_node = searched_node.next()  # see if the AS node is already in the db or not. If yes, cur_node == prev_node
#         except StopIteration:
#             cur_node = Node('asn', label=str(asn))  # if not exists, then create a new one
#         if index > 0:
#             if index == len(path) - 1:
#                 cur_node['path'] = path  # attach AS path to the last ASN
#             if cur_node != prev_node:
#                 if counter_as_prepend > 0:
#                     cur_node['prepended'] = counter_as_prepend
#                     counter_as_prepend = 0  # reset
#                 peering = Relationship(cur_node, 'PEER', prev_node)
#                 peering['time'] = time
#                 graph.create(peering)
#             else:  # AS prepending
#                 counter_as_prepend += 1
#         prev_node = cur_node
