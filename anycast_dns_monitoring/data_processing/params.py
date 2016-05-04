from enum import Enum

measurement_id = '2048556'
base_uri = 'https://atlas.ripe.net/api/v1/'
db = 'anycast_monitoring'

class RipeAtlasData(Enum):
    """
    enumeration of data types taken from RIPE Atlas
    """
    traceroute = 0
    chaos = 1
    probes = 2
