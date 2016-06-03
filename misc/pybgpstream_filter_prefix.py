import time
from _pybgpstream import BGPStream, BGPRecord, BGPElem

start_time = time.time()

stream = BGPStream()
rec = BGPRecord()

stream.add_filter('prefix','140.78.0.0/16')
stream.add_filter('record-type','ribs')
stream.add_filter('collector','rrc11')
# stream.add_filter('project','ris')
stream.add_interval_filter(1464681000, 1464682200)  # 1464682200 ==> 05/31/2016 @ 8:10am (UTC)

stream.start()
#
# while(stream.get_next_record(rec)):
#     # Print the record information only if it is not a valid record
#     if rec.status == "valid":
#         elem = rec.get_next_elem()
#         while elem:
#             # Print record and elem information
#             print rec.collector, elem.peer_address, elem.peer_asn, elem.fields['as-path']
#             elem = rec.get_next_elem()

result = []
while stream.get_next_record(rec):
    if rec.status == "valid":
        elem = rec.get_next_elem()
        while elem:
            print rec.collector, elem.type, elem.peer_address, elem.peer_asn, elem.fields
            as_path = elem.fields['as-path'].split()
            as_path.append(' ')  # for tree creation
            result.append(as_path)
            elem = rec.get_next_elem()

print('-- elapsed time: {} seconds'.format(time.time() - start_time))
print(result)