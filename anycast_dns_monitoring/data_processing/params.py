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
# root_prefix = {
#     'a': '198.41.0.0/24',
#     'b': '192.228.79.0/24',
#     'c': '192.33.4.0/24',
#     'd': '199.7.91.0/24',
#     'e': '192.203.230.0/24',
#     'f': '192.5.5.0/24',
#     'g': '192.112.36.0/24',
#     'h': '198.97.190.0/24',
#     'i': '192.36.148.0/24',
#     'j': '192.58.128.0/24',
#     'k': '193.0.14.0/24',
#     'l': '199.7.83.0/24',
#     'm': '202.12.27.0/24'
# }

# root_prefix6 = {
#     'a': '2001:503:ba3e::/48',
#     'b': '2001:500:84::/48',
#     'c': '2001:500:2::/48',
#     'd': '2001:500:2d::/48',
#     'e': '',
#     'f': '2001:500:2f::/48',
#     'g': '',
#     'h': '2001:500:1::/48',
#     'i': '2001:7fe::/33',
#     'j': '2001:503:c27::/48',
#     'k': '2001:7fd::/48',
#     'l': '2001:500:9f::/48',
#     'm': '2001:dc3::/32'
# }


def root_prefix(root, timestamp):
    if root == 'a':
        return '198.41.0.4'
    if root == 'b':  # not anycasted. ignore
        return ''
    if root == 'c':
        return '192.33.4.12'
    if root == 'd':
        if timestamp < 1357171200:  # 2013-01-03
            return '128.8.10.90'
        else:
            return '199.7.91.13'
    if root == 'e':
        return '192.203.230.10'
    if root == 'f':
        return '192.5.5.241'
    if root == 'g':
        return '192.112.36.4'
    if root == 'h':
        if timestamp < 1448928000:  # 2015-12-01
            return '128.63.2.53'
        else:
            return '198.97.190.53'
    if root == 'i':
        return '192.36.148.17'
    if root == 'j':
        return '192.58.128.30'
    if root == 'k':
        return '193.0.14.129'
    if root == 'l':
        if timestamp < 1193875200:  # 2007-11-01
            return '198.32.64.12'
        else:
            return '199.7.83.42'
    if root == 'm':
        return '202.12.27.33'


def root_prefix6(root, timestamp):
    if root == 'a':
        if timestamp < 1201651200:
            return ''
        return '2001:503:BA3E::2:30'
    if root == 'b':  # not anycasted
        return ''
    if root == 'c':
        return '2001:500:2::C'
    if root == 'd':
        return '2001:500:2D::D'
    if root == 'e':
        return ''
    if root == 'f':
        if timestamp < 1201651200:
            return ''
        return '2001:500:2f::f'
    if root == 'g':
        return ''
    if root == 'h':
        if timestamp < 1201651200:
            return ''
        return '2001:500:1::53'
    if root == 'i':
        return '2001:7fe::53'
    if root == 'j':
        if timestamp < 1201651200:
            return ''
        return '2001:503:c27::2:30'
    if root == 'k':
        if timestamp < 1201651200:
            return ''
        return '2001:7fd::1'
    if root == 'l':
        if timestamp < 1458691200:  # 2016-3-23
            return '2001:500:3::42'
        else:
            return '2001:500:9f::42'
    if root == 'm':
        if timestamp < 1201651200:
            return ''
        return '2001:dc3::35'


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