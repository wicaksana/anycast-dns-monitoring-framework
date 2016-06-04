from _pybgpstream import BGPRecord, BGPStream


stop = 1422778200
start = stop - 1200  # 15000 second seems to be the shortest interval to get data from BGPstream

result = []

stream = BGPStream()
rec = BGPRecord()

stream.add_filter('prefix', '192.33.4.0/24')
stream.add_filter('record-type', 'ribs')
stream.add_filter('project', 'ris')
# stream.add_filter('collector', 'router-route-views.routeviews.org.peer-IPV4_route-spews.cbbtier3.att.net')
stream.add_interval_filter(start, stop)

stream.start()
print('start')
# test = stream.get_data_interfaces()
# print('test: {}'.format(test))

while stream.get_next_record(rec):
    if rec.status == "valid":
        elem = rec.get_next_elem()
        while elem:
            as_path = elem.fields['as-path'].split()
            as_path.append(' ')  # for tree creation
            result.append(as_path)
            elem = rec.get_next_elem()

print(result)