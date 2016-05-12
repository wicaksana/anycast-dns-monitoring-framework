from enum import Enum

# traceroute and CHAOS measurement IDs for C-Root, both for IPv4 and IPv6
traceroute_id = '5011'
traceroute6_id = '6011'
chaos_id = '10511'
chaos6_id = '11411'

root_asn = '2149'  # C-Root ASN
prefix = '192.33.4.12/24'  # C-Root
prefix6 = '2001:500:2::c/32'  # C-Root

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