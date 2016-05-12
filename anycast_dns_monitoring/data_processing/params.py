from enum import Enum

traceroute_id = '2048556'  # random
traceroute6_id = '3787166'  # random
chaos_id = '10511'
chaos6_id = '11411'

root_asn = '47065'
prefix = '140.78.0.0/16'  # random
prefix6 = '2001:608::/32'  # random

atlas_uri = 'https://atlas.ripe.net/api/v1/'
ris_uri = 'https://stat.ripe.net/data/'

# database-related
db = 'anycast_monitoring'
map4 = 'prefix_asn_mapping'
map6 = 'prefix_asn_mapping6'
probes = 'probes'


class RipeAtlasData(Enum):
    """
    enumeration of data types taken from RIPE Atlas
    """
    traceroute = 0
    chaos = 1
    probes = 2


class Version(Enum):
    """
    enumeration for ipv4 and ipv6
    """
    ipv4 = 0
    ipv6 = 1