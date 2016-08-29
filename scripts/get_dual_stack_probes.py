import requests
from datetime import datetime

base_url = 'https://atlas.ripe.net/api/v1/probe/?limit=100'
next_url = ''

result = []

counter = 0
earliest_join = None

while next_url is not None:
    data = requests.get(base_url).json()
    next_url = data['meta']['next']

    for probe in data['objects']:
        # if probe['status'] == 1 and probe['address_v6'] and probe['first_connected'] < 1293840000:
        if probe['status'] == 1 and probe['address_v6'] and probe['first_connected'] < 1325376000:
            first_connected = datetime.fromtimestamp(probe['first_connected']).strftime('%Y-%m-%d')
            print('ID: {} IPv4: {} IPv6: {} since: {} Country: {}'
                  .format(probe['id'],
                          probe['address_v4'],
                          probe['address_v6'],
                          first_connected,
                          probe['country_code']))
            counter += 1
    if next_url is not None:
        base_url = 'https://atlas.ripe.net' + next_url

print('\nTotal dual-stack probes: {}'.format(counter))