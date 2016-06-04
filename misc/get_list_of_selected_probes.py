# -*- coding: utf-8 -*-
from pymongo import MongoClient


def main():
    country_cities = {
        'NL': ['Amsterdam'],
        'GB': ['London'],
        'FR': ['Paris'],
        'CH': ['Geneva', 'Zurich'],
        'AT': ['Vienna'],
        'JP': ['Tokyo'],
        'SE': ['Stockholm'],
        'US': ['San Jose', 'New York', 'Palo Alto', 'Miami', 'Oregon', 'Atalanta', 'Ashburn', 'San Fransisco'],
        'IT': ['Milan'],
        'DE': ['Frankfurt'],
        'RU': ['Moscow'],
        'BR': ['Sao Paulo'],
        'AU': ['Perth', 'Sydney'],
        'KE': ['Nairobi'],
        'SG': ['Singapore'],
        'ZA': ['Johannesburg'],
        'RS': ['Belgrade']
    }

    client = MongoClient()
    anycast = client.anycast_monitoring
    probes = anycast.probes

    with open('probe_list2.txt', 'w') as output_file:
        for country in country_cities:
            for city in country_cities[country]:
                counter = 0
                results = probes.find({'$text': {'$search': city}})
                for result in results:
                    if result['country_code'] == country:
                        # output_file.write('{}\t{}\n'.format(result['prb_id'], result['address'].encode('utf8')))
                        output_file.write('{},{}\n'.format(result['latitude'], result['longitude']))
                        counter += 1
                print('City: {}, total probes: {}'.format(city, counter))


if __name__ == '__main__':
    main()