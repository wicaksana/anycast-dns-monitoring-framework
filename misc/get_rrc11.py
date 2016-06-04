import requests

url = 'https://stat.ripe.net/data/looking-glass/data.json?resource=140.78.0.0/16'

data = requests.get(url=url).json()

rrc11 = data['data']['rrcs']['RRC11']

for entry in rrc11['entries']:
    print("peer: {}, as path: {}".format(entry['update_from'], entry['as_path']))

rrcs = rrc11 = data['data']['rrcs']

for rrc in rrcs:
    print(rrc)