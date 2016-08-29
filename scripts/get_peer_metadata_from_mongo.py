from pymongo import MongoClient
from py2neo import Graph
import requests

client = MongoClient()
anycast = client.anycast_monitoring
peer_data = anycast.peer_data

graph = Graph(password='neo4jneo4j')

# use ground truth: K-Root and timestamp = 1325376000
timestamp = 1325376000
prefixes = ['193.0.14.0/24', '2001:7fd::/48']

peer4 = peer_data.find({'timestamp': timestamp, 'prefix': prefixes[0]})
peer6 = peer_data.find({'timestamp': timestamp, 'prefix': prefixes[1]})

for p1 in peer4:
    try:
        keys4 = set().union(*(d.keys() for d in p1['peers']))
    except:
        keys4 = set()

for p2 in peer6:
    try:
        keys6 = set().union(*(d.keys() for d in p2['peers']))
    except:
        keys6 = set()

common_peers = list(set(keys4) & set(keys6))

url = 'https://stat.ripe.net/data/bgp-state/data.json?resource={0}&timestamp={1}'.format(prefixes[0], timestamp)
data = requests.get(url).json()

for peer in common_peers:
    query = ''

print(common_peers)
# print(len(common_peers))