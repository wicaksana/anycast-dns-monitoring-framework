from _pybgpstream import BGPStream, BGPRecord
from collections import defaultdict

# MOAS: multiple origin AS

stream = BGPStream()
rec = BGPRecord()

stream.add_filter('collector', 'route-views.sg')
stream.add_filter('record-type', 'ribs')
stream.add_interval_filter(1438415400,1438416600)  # Sat, 01 Aug 2015 7:50:00 GMT -  08:10:00 GMT

stream.start()

prefix_origin = defaultdict(set)

while stream.get_next_record(rec):
    elem = rec.get_next_elem()
    while elem:
        # get the prefix
        pfx = elem.fields['prefix']
        # get the list of ASes in the AS path
        ases = elem.fields['as-path'].split(" ")

        if len(ases) > 0:
            origin = ases[-1]
            prefix_origin[pfx].add(origin)

        elem = rec.get_next_elem()

for pfx in prefix_origin:
    if len(prefix_origin[pfx]) > 1:
        print('{}, {}'.format(pfx, prefix_origin[pfx]))