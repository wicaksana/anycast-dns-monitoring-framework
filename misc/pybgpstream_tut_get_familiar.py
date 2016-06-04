from _pybgpstream import BGPStream, BGPRecord, BGPElem


stream = BGPStream()
rec = BGPRecord()

stream.add_filter('collector', 'rrc11')
stream.add_interval_filter(1438446000, 1438446000)  # 08/01/2015 @ 8:20am (UTC)

stream.start()

# get next record
while stream.get_next_record(rec):
    if rec.status != 'valid':
        print('invalid: {} {} {} {} {}'.format(rec.project, rec.collector, rec.type, rec.time, rec.status))
    else:
        elem = rec.get_next_elem()
        # print('[*] dump time: {} - dump position: {}'.format(rec.dump_time, rec.dump_position))
        while elem:
            # the following two lines are the original ones
            # print('rec: {} | {} | {} | {} | {} '.format(rec.project, rec.collector, rec.type, rec.time, rec.status))
            # print('elem: {} | {} | {} | {} '.format(elem.type, elem.peer_address, elem.peer_asn, elem.fields))

            # modified
            print('Type: {} Peer ASN: {}'.format(elem.type, elem.peer_asn))
            print('- prefix: {}'.format(elem.fields['prefix']))
            print('- AS path: {}'.format(elem.fields['as-path']))
            communities = []
            for comm in elem.fields['communities']:
                communities.append('{}:{}'.format(comm['asn'], comm['value']))
            print('- community: {}'.format(communities))

            elem = rec.get_next_elem()