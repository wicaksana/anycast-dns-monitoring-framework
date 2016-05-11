from enum import Enum

msmnt_id = '2048556'  # measurement id for IPv4 prefix
msmnt_id6 = '3787166'  # measurement ID for IPv6 prefix. Not yet decided. use this temporarily
atlas_uri = 'https://atlas.ripe.net/api/v1/'
ris_uri = 'https://stat.ripe.net/data/'

# database-related
db = 'anycast_monitoring'
map4 = 'prefix_asn_mapping'
map6 = 'prefix_asn_mapping6'
probes = 'probes'

peering_asn = '47065'
prefix = '140.78.0.0/16'  # anycast prefix. 140.78.0.0/16 is for testing only
prefix6 = '2001:608::/32'  # anycast IPv6 prefix. for testing only


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