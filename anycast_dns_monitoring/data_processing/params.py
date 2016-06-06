from enum import Enum

# traceroute and CHAOS measurement IDs for C-Root, both for IPv4 and IPv6
traceroute_id = '5011'
traceroute6_id = '6011'
chaos_id = '10511'
chaos6_id = '11411'

root_asn = '2149'
ip = '192.33.4.12'
ip6 = '2001:500:2::c'
prefix = '192.33.4.0/24'
prefix6 = '2001:500:2::/48'

atlas_uri = 'https://atlas.ripe.net/api/v1/'
ris_uri = 'https://stat.ripe.net/data/'

# database-related
db = 'anycast_monitoring'
map4 = 'prefix_asn_mapping'
map6 = 'prefix_asn_mapping6'
probes = 'probes'

# root-server to its prefixes
root_prefix = {
    'a': '198.41.0.0/24',
    'b': '192.228.79.0/24',
    'c': '192.33.4.0/24',
    'd': '199.7.91.0/24',
    'e': '192.203.230.0/24',
    'f': '192.5.5.0/24',
    'g': '192.112.36.0/24',
    'h': '198.97.190.0/24',
    'i': '192.36.148.0/24',
    'j': '192.58.128.0/24',
    'k': '193.0.14.0/24',
    'l': '199.7.83.0/24',
    'm': '202.12.27.0/24'
}

root_prefix6 = {
    'a': '2001:503:ba3e::/48',
    'b': '2001:500:84::/48',
    'c': '2001:500:2::/48',
    'd': '2001:500:2d::/48',
    'e': '',
    'f': '2001:500:2f::/48',
    'g': '',
    'h': '2001:500:1::/48',
    'i': '2001:7fe::/33',
    'j': '2001:503:c27::/48',
    'k': '2001:7fd::/48',
    'l': '2001:500:9f::/48',
    'm': '2001:dc3::/32'
}


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