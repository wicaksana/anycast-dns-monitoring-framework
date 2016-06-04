import requests
from pprint import pprint

# mrmnt_result = 'https://atlas.ripe.net/api/v1/measurement/2048556/?fields='
# mrmnt_result = 'https://atlas.ripe.net/api/v1/measurement-latest/2048556/' # latest measurement
# mrmnt_result = 'https://atlas.ripe.net/api/v1/measurement/2048556/?fields=probes' # latest measurement
# mrmnt_result = 'https://atlas.ripe.net/api/v1/measurement/2048556/result/?start=1459946820&stop=1459948020' # latest measurement
mrmnt_result = 'https://atlas.ripe.net/api/v1/measurement/3787166/result/?start=1462796742&stop=1462797042' # ipv6
r = requests.get(mrmnt_result)
pprint(r.json())
