# -*- coding: utf-8 -*-
import sys
import time
from pymongo import MongoClient
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderServiceError

def main():
    client = MongoClient()
    anycast = client.anycast_monitoring
    probes = anycast.probes

    # geolocator = GoogleV3(api_key='AIzaSyA00iYEw_o-k3G7qrubxxsEc_8qY1w1PAk')
    geolocator = GoogleV3()

    for probe in probes.find():
        if probe['latitude'] is not None and probe['longitude'] is not None:
            if 'address' not in probe or probe['address'] is None:
                try:
                    addr = geolocator.reverse('{}, {}'.format(probe['latitude'], probe['longitude']))
                    try:
                        address = addr[4].__str__()
                    except UnicodeEncodeError:
                        print('UnicodeEncodeError -- lat:{}  lon:{}'.format(probe['latitude'], probe['longitude']))
                        sys.exit(1)
                    except IndexError:
                        address = addr[0].__str__()
                    except TypeError, e:
                        print('TypeError lat:{}  lon:{} ==> {}'.format(probe['latitude'], probe['longitude'], e))
                        address = None
                    # addr = unicode(addr, 'utf-8')
                    # print(addr)
                    probes.update({'prb_id': probe['prb_id']}, {'$set': {'address': address}})
                except GeocoderServiceError:
                    print('stopped at {}'.format(probe['prb_id']))
                    sys.exit(1)
                time.sleep(0.1)

if __name__ == '__main__':
    main()

