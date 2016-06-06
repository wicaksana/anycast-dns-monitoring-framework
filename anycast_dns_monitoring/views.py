from datetime import datetime
from anycast_dns_monitoring import app, api
from flask import render_template
from flask import jsonify
from flask import send_from_directory
from flask_restful import Resource
from py2neo import Graph

import time
import pytz

from anycast_dns_monitoring.data_processing.ris import Ris
from anycast_dns_monitoring.data_processing.ripe_atlas import RipeAtlas, Version
from anycast_dns_monitoring.data_processing.params import root_prefix, root_prefix6

# graph initialization
graph = Graph(password='neo4jneo4j')


@app.route('/')
def index():
    """
    default page route
    :return:
    """
    return render_template('index.html')


# @app.route('/json/<path:path>')
# def get_json(path):
#     return send_from_directory('static/json', path)


@app.route('/graph/<string:root>/<string:version>/<ts>')
def get_graph(root, version, ts):
    month, year = ts.split('-')
    dt = datetime(int(year), int(month), 1, 1, 0, 0)  # day 1 of each month 01:00 AM (UTC+1)
    utc = pytz.utc
    utc_dt = utc.localize(dt)
    timestamp = int(time.mktime(utc_dt.timetuple()))

    if version == '4':
        prefix = root_prefix[root]
    elif version == '6':
        prefix = root_prefix6[root]
    else:
        prefix = ''

    query = 'MATCH (d:asn)<-[r:TO]-(s:asn) ' \
            'WHERE r.time={0} AND r.prefix="{1}" ' \
            'RETURN d.name as asn_a, s.name as asn_b, r.prepended as prepended '.format(timestamp, prefix)
    print('query: {}'.format(query))
    results = graph.run(query)

    origin_as = None
    query = 'MATCH (:asn)-[:TO{{time:{0}, prefix:"{1}"}}]->(d:asn) ' \
            'WHERE NOT (d)-[:TO{{time:{0}, prefix:"{1}"}}]->() ' \
            'RETURN DISTINCT d.name as origin'.format(timestamp, prefix)
    origin = graph.run(query)
    print('query: {}'.format(query))

    for ori in origin:
        origin_as = ori['origin']

    query = 'MATCH p=(d:asn{{name:"{0}"}})<-[r:TO*{{time:{1}, prefix:"{2}"}}]-(s:asn) ' \
            'RETURN DISTINCT s.name as asn, length(p) as degree'.format(origin_as, timestamp, prefix)
    degrees = graph.run(query)
    print('query: {}'.format(query))

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

    # attach AS degrees
    for asn, degree in degrees:
        nodes[nodes.index({'title': asn})]['degree'] = degree

    # origin AS
    # todo: add exception handler: ValueError: {'title': None} is not in list
    try:
        nodes[nodes.index({'title': origin_as})]['degree'] = 0
    except ValueError as e:
        print('[!] {0}'.format(e))

    return jsonify({'nodes': nodes, 'links': rels})


class ControlPlane(Resource):
    # TODO: add exception handler
    def get(self, version, datetime):
        print('version: {}'.format(version))
        print('datetime: {}'.format(datetime))

        if version == 'ipv4':
            msmnt = Ris(Version.ipv4)
        elif version == 'ipv6':
            msmnt = Ris(Version.ipv6)
        else:
            return 'IP version is incorrect'

        if datetime == 'latest':
            result = msmnt.tree_control_plane()
        else:
            result = msmnt.tree_control_plane(datetime=datetime)

        return jsonify(result=result)


class DataPlane(Resource):
    def get(self, version, datetime):
        if version == 'ipv4':
            msmnt = RipeAtlas(Version.ipv4)
        elif version == 'ipv6':
            msmnt = RipeAtlas(Version.ipv6)
        else:
            return 'IP version is incorrect'

        if datetime == 'latest':
            result = msmnt.tree_data_plane()
        else:
            result = msmnt.tree_data_plane(datetime=datetime)

        return jsonify(result=result)


api.add_resource(ControlPlane, '/control-plane/<string:version>/<string:datetime>')
api.add_resource(DataPlane, '/data-plane/<string:version>/<string:datetime>')