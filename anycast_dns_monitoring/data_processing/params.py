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

# mapping collector code to its description
col_map = {
    '00': 'RIPE NCC (Ams)',
    '01': 'LINX, London',
    '02': 'SFINX, Paris',
    '03': 'AMS-IX & NL-IX',
    '04': 'CIXP, Geneva',
    '05': 'VIX, Vienna',
    '06': 'Otemachi, Japan',
    '07': 'Stockholm, Sweden',
    '08': 'San Jose (CA), USA',
    '09': 'Zurich, Switzerland',
    '10': 'Milan, Italy',
    '11': 'New York (NY), USA',
    '12': 'Frankfurt, Germany',
    '13': 'Moscow, Russia',
    '14': 'Palo Alto, USA',
    '15': 'Sao Paulo, Brazil',
    '16': 'Miami, USA',
    '18': 'CATNIX, Barcelona',
    '19': 'NAP Africa Johannesburg',
    '20': 'SwissIX, Zurich',
    '21': 'France-IX, Paris',
}

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