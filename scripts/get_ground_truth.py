import requests
from pprint import pprint

'''
this script is used to validate Neo4j query
'''

url = 'https://stat.ripe.net/data/bgp-state/data.json?timestamp=1325376000&resource=193.0.14.0/24'

data = requests.get(url).json()
# pprint(data)
result = set()

for path in data['data']['bgp_state']:
    result.add(path['path'][0])

# print(result)
print(sorted(result))
print(len(result))
