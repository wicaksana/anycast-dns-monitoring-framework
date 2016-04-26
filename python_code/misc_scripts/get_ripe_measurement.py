#!/usr/env python3

import requests
from pprint import pprint

mrmnt_result = 'https://atlas.ripe.net/api/v1/measurement/2048556/?fields='
r = requests.get(mrmnt_result)
probes = r.json()['probes']

probe_0 = 'https://atlas.ripe.net'
s = requests.get(probe_0 + probes[0]['url'])
print(s.json())