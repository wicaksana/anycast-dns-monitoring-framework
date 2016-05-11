import subprocess
import anycast_dns_monitoring.data_processing.params as params


def get_asn(prefix):
    """
    get ASN from a certain prefix
    :param prefix:
    :return:
    """
    cmd = 'whois -h whois.cymru.com "{0}"'.format(prefix)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    line = process.stdout.readlines()[1].decode('utf-8')
    res = [x.strip() for x in line.split('|')]
    result = dict()
    result['asn'] = res[0]
    result['prefix'] = res[1]
    result['info'] = res[2]

    return result


def get_bulk_asn(prefix_list):
    """
    https://gist.github.com/ttreitlinger/976700
    get ASNs from bulk of prefixes
    :param prefix_list: list of prefixes
    :return:
    """
    #TODO: implementation

    with open('temp.txt', 'w') as input_file:
        input_file.write('begin\n')
        input_file.write('verbose\n')
        for ip in prefix_list:
            if not ip.startswith('::f'):  # ignore link-local address
                input_file.write('{}\n'.format(ip))
        input_file.write('end\n')

    cmd = 'netcat whois.cymru.com 43 < temp.txt'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = [x.decode('utf-8') for x in process.stdout.readlines()[1:]]

    result = []

    for line in lines:
        res = [x.strip() for x in line.split('|')]
        res2 = dict()
        res2['ip'] = res[1]
        res2['asn'] = res[0]
        res2['prefix'] = res[2].split('/')[0]
        res2['info'] = res[6]
        result.append(res2)

    return result


def write_to_db(db, data):
    """
    write data to database
    :param db:
    :param data:
    :return: None
    """
    db.drop_collection(col=params.map6)  # drop first
    db.insert_many(col=params.map6, data=data)

