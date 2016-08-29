import requests
from pprint import pprint

base_url = 'https://stat.ripe.net/data/ris-peerings/data.json?'
timestamp = 1325376000
prefixes = ['193.0.14.0/24', '2001:7fd::/48']  # K-Root

result = []

for index, prefix in enumerate(prefixes):
    params = 'resource={0}&query_time={1}'.format(prefix, timestamp)

    url = base_url + params

    data = requests.get(url).json()
    # pprint(data['data']['peerings'])
    result.append([])
    for peers in data['data']['peerings']:
        probe = peers['probe']['ixp']
        p = []
        for peer in peers['peers']:
            p.append(peer['asn'])
        result[index].append({'probe': probe, 'peers': p})


# are peers in IPv4 and IPv6 different?
for peer4, peer6 in zip(result[0], result[1]):
    print('probe {} - peers: {}'.format(peer4['probe'], peer4['peers']))
    print('probe {} - peers: {}\n'.format(peer6['probe'], peer6['peers']))


# Is there any sort of dual-stack peers for each probe?
print('[*] Common peers (IPv4/IPv6):')
for peer4, peer6 in zip(result[0], result[1]):
    common_set = set(peer4['peers']) & set(peer6['peers'])
    print('probe {} - Common peers: {}'.format(peer4['probe'], common_set))