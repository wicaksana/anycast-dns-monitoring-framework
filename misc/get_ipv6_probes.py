from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    anycast = client.anycast_monitoring
    probes = anycast.probes

    ipv6_probes = probes.find({'asn6': {"$ne": None }})

    for probe in ipv6_probes:
        print(probe)