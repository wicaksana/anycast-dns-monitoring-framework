from datetime import datetime
from anycast_dns_monitoring import app
from flask import render_template
from flask import jsonify
from py2neo import Graph
from pymongo import MongoClient
import time
import pytz
import requests
import os
from collections import defaultdict
from datetime import datetime
import pandas as pd
from pandas import DataFrame

from anycast_dns_monitoring.data_processing.params import root_prefix, root_prefix6


# graph initialization
graph = Graph(password='neo4jneo4j')

# mongodb initialization
client = MongoClient()
anycast = client.anycast_monitoring
peer_data = anycast.peer_data


@app.route('/')
def index():
    """
    default page route
    :return: index.html
    """
    return render_template('index.html')

@app.route('/for_science/')
def scientific_stuff():
    """
    return page dedicated for anything needed for scientific stuff in my thesis
    :return:
    """
    return render_template('thesis.html')


@app.route('/graph/<string:root>/<string:version>/<ts>')
def get_graph(root, version, ts):
    """
    get data required to draw main graph
    :param root:
    :param version:
    :param ts:
    :return: array of nodes and links
    """
    timestamp = convert_timestamp(ts)

    if version == '4':
        prefix = root_prefix(root, timestamp)
    elif version == '6':
        prefix = root_prefix6(root, timestamp)
    else:
        prefix = ''

    # Get all nodes for tree graph
    query = 'MATCH (d:asn)<-[r:TO]-(s:asn) ' \
            'WHERE r.time={0} AND r.prefix="{1}" ' \
            'RETURN DISTINCT d.name as asn_a, s.name as asn_b, r.prepended as prepended '.format(timestamp, prefix)
    print('query tree: {}'.format(query))
    results = graph.run(query)

    if not results:
        print('Empty result.')
        return jsonify({'nodes': [], 'links': []})

    origin_as = []
    # get origin AS
    query = 'MATCH (:asn)-[:TO{{time:{0}, prefix:"{1}"}}]->(d:asn) ' \
            'WHERE NOT (d)-[:TO{{time:{0}, prefix:"{1}"}}]->() ' \
            'RETURN DISTINCT d.name as origin'.format(timestamp, prefix)
    origin = graph.run(query)
    print('query origin: {}'.format(query))

    for ori in origin:
        origin_as.append(ori['origin'])

    nodes = []
    rels = []

    for asn_a, asn_b, prepended in results:
        try:
            target = nodes.index({'title': asn_a})
        except ValueError:
            nodes.append({'title': asn_a})
            target = nodes.index({'title': asn_a})
        src_asn = {'title': asn_b}
        try:
            src = nodes.index(src_asn)
        except ValueError:
            nodes.append(src_asn)
            src = nodes.index(src_asn)
        rels.append({'source': src, 'target': target, 'prepended': prepended})

    # origin AS
    for origin in origin_as:
        try:
            nodes[nodes.index({'title': origin})]['degree'] = 0
            # get nodes degree
            query = 'MATCH p=(d:asn{{name:"{0}"}})<-[r:TO*{{time:{1}, prefix:"{2}"}}]-(s:asn) ' \
                    'RETURN DISTINCT s.name as asn, length(p) as degree'.format(origin, timestamp, prefix)
            degrees = graph.run(query)
            print('query degrees: {}'.format(query))

            for asn, degree in degrees:
                try:
                    nodes[nodes.index({'title': asn})]['degree'] = degree
                except ValueError:  # it means the node has already appended with degree information
                    # print('[!] error attaching as degree: {}'.format(e))
                    pass
        except ValueError as e:
            print('[!] {0}'.format(e))

    return jsonify({'nodes': nodes, 'links': rels})


@app.route('/mutual_peers/<string:root>/<ts>')
def get_mutual_peers(root, ts):
    """
    get mutual peers statistics for a given timestamp and a Root Server
    :param root:
    :param ts:
    :return: array of mutual peers, mutual peers with identical AS path, mutual peers with same AS path length but
    different AS path, mutual peers with longer IPv4 path, mutual peers with shorter IPv4 path
    """
    timestamp = convert_timestamp(ts)
    prefix4 = root_prefix(root, timestamp)
    prefix6 = root_prefix6(root, timestamp)

    bgp_state4, peer4 = get_peers(prefix4, timestamp)
    bgp_state6, peer6 = get_peers(prefix6, timestamp)

    mutual_peers = list(set(peer4) & set(peer6))

    peers_mutual, peers_identical, peers_diff_path, peers_v4_longer, peers_v4_shorter = \
        get_peers_stat(mutual_peers, bgp_state4, bgp_state6)

    return jsonify({'peers_mutual': peers_mutual,
                    'peers_identical': peers_identical,
                    'peers_diff_path': peers_diff_path,
                    'peers_v4_longer': peers_v4_longer,
                    'peers_v4_shorter': peers_v4_shorter
                    })

###################################
# For 'scientific' part
###################################


@app.route('/boxplot/<string:root>')
def get_boxplot(root):
    """
    get boxplot data
    :param root: Root Server (in alphabet)
    :return:
    """
    container4 = {}
    container6 = {}

    for file in sorted(os.listdir('datasets/{}/'.format(root))):
        timestamp = int(file.split('-')[0])
        filename = 'datasets/{0}/{1}'.format(root, file)
        opened_file = DataFrame.from_csv(filename, sep='\t')
        if not opened_file.empty:
            res4 = opened_file['len4']
            container4[timestamp] = res4
            res6 = opened_file['len6']
            container6[timestamp] = res6
        else:
            container4[timestamp] = pd.Series()
            container6[timestamp] = pd.Series()

    df4 = DataFrame.from_dict(container4)
    df6 = DataFrame.from_dict(container6)

    dict4 = defaultdict()
    dict6 = defaultdict()

    #######
    # IPv4
    #######
    for ts in df4:
        dict4[ts] = {
            'name': datetime.fromtimestamp(ts).strftime('%Y-%m-%d'),
            'type': 'box',
            'y': [int(i) for i in df4[ts].dropna()]
        }
    result4 = [dict4[i] for i in dict4]

    #######
    # IPv6
    #######
    for ts in df6:
        dict6[ts] = {
            'name': datetime.fromtimestamp(ts).strftime('%Y-%m-%d'),
            'type': 'box',
            'y': [int(i) for i in df6[ts].dropna()]
        }
    result6 = [dict6[i] for i in dict6]

    return jsonify({'ipv4': result4, 'ipv6': result6})


@app.route('/stacked-bar/<string:root>')
def get_stacked_bar(root):
    """
    get required data for stacked bar visualization
    :param root:
    :return:
    """
    container4 = {}
    container6 = {}

    for file in sorted(os.listdir('datasets/{}/'.format(root))):
        timestamp = int(file.split('-')[0])
        filename = 'datasets/{0}/{1}'.format(root, file)
        opened_file = DataFrame.from_csv(filename, sep='\t')
        if not opened_file.empty:
            res4 = opened_file['len4'].value_counts()
            container4[timestamp] = res4
            res6 = opened_file['len6'].value_counts()
            container6[timestamp] = res6
        else:
            container4[timestamp] = pd.Series()
            container6[timestamp] = pd.Series()

    # print(container4)
    dict4 = defaultdict()
    dict6 = defaultdict()

    ts = [datetime.fromtimestamp(i).strftime('%Y-%m-%d') for i in sorted(container4)]

    ###
    # IPv4
    ##
    # get maximum hop
    max4 = 0
    for item in container4:
        for i in container4[item].iteritems():
            max4 = max(max4, int(i[0]))

    # initialize returned result
    for hop in range(1, max4 + 1):
        dict4[hop] = {'x': ts, 'y': [], 'name': hop, 'type': 'bar'}

    # appending the result
    for res in sorted(container4):
        temp_res = dict()
        for item in container4[res].iteritems():
            temp_res[int(item[0])] = int(item[1])

        for res_item in dict4.items():
            if res_item[1]['name'] in temp_res:
                res_item[1]['y'].append(temp_res[res_item[1]['name']])
            else:
                res_item[1]['y'].append(0)

    result4 = [dict4[i] for i in dict4]

    ###
    # IPv6
    ##
    # get maximum hop
    max6 = 0
    for item in container6:
        for i in container6[item].iteritems():
            max6 = max(max6, int(i[0]))

    # initialize returned result
    for hop in range(1, max6 + 1):
        dict6[hop] = {'x': ts, 'y': [], 'name': hop, 'type': 'bar'}

    # appending the result
    for res in sorted(container6):
        temp_res = dict()
        for item in container6[res].iteritems():
            temp_res[int(item[0])] = int(item[1])

        for res_item in dict6.items():
            if res_item[1]['name'] in temp_res:
                res_item[1]['y'].append(temp_res[res_item[1]['name']])
            else:
                res_item[1]['y'].append(0)

    result6 = [dict6[i] for i in dict6]

    return jsonify({'ipv4': result4, 'ipv6': result6})


########################################################################################################################
# Helper methods
########################################################################################################################


def convert_timestamp(ts):
    """
    convert timestamp from js app to unix timestamp
    :param ts: MM/YYYY
    :return: unix timestamp
    """
    month, year = ts.split('-')
    dt = datetime(int(year), int(month), 1, 1, 0, 0)  # day 1 of each month 01:00 AM (UTC+1)
    utc = pytz.utc
    utc_dt = utc.localize(dt)
    timestamp = int(time.mktime(utc_dt.timetuple()))

    return timestamp


def get_peers(prefix, timestamp):
    """
    helper method to extract peers from RIPE RIS' bgp_data
    :return:
    """
    url = 'https://stat.ripe.net/data/bgp-state/data.json?resource={0}&timestamp={1}'.format(prefix, timestamp)
    print('get_peers {}'.format(url))
    data = requests.get(url).json()
    data = data['data']['bgp_state']

    bgp_state = []
    if data:
        for item in data:
            route_info = {
                'peer': item['path'][0],
                'root': item['path'][-1],
                'as_path': list(deduplicate(item['path']))
            }
            bgp_state.append(route_info)

    peer = [item['peer'] for item in bgp_state]

    return bgp_state, peer


def get_peers_stat(peers, bgp_state4, bgp_state6):
    """
    get mutual peers statistics
    :param peers:
    :param bgp_state4:
    :param bgp_state6:
    :return:
    """
    container = []
    for peer in sorted(peers):
        try:
            path4 = [d['as_path'] for d in bgp_state4 if d['peer'] == peer][0]
        except KeyError:
            print('[!] no result from RIS. path4 is empty')
            path4 = []
        try:
            path6 = [d['as_path'] for d in bgp_state6 if d['peer'] == peer][0]
        except KeyError:
            print('[!] no result from RIS. path6 is empty')
            path6 = []
        similar = 1 if path4 == path6 else 0
        temp_res = {
            'peer': peer,
            'similar': similar,
            'path4': path4,
            'path6': path6
        }
        container.append(temp_res)

    result_all = sorted([i['peer'] for i in container])
    result_identical = sorted([i['peer'] for i in container if i['similar'] == 1])
    result_diff = sorted([i['peer'] for i in container if len(i['path4']) == len(i['path6']) and i['similar'] == 0])
    result_v4_longer = sorted([i['peer'] for i in container if len(i['path4']) > len(i['path6'])])
    result_v4_shorter = sorted([i['peer'] for i in container if len(i['path4']) < len(i['path6'])])

    return result_all, result_identical, result_diff, result_v4_longer, result_v4_shorter


def deduplicate(items):
    """
    to remove AS prepending
    :param items:
    :return: deduplicate AS path
    """
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)