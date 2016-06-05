from anycast_dns_monitoring import app, api
from flask import render_template
from flask import jsonify
from flask import send_from_directory
from flask_restful import Resource
from py2neo import Graph

from anycast_dns_monitoring.data_processing.ris import Ris
from anycast_dns_monitoring.data_processing.ripe_atlas import RipeAtlas, Version

# graph initialization
graph = Graph(password='neo4jneo4j')
prefix = '2001:7fe::/33'
timestamp = 1422748800


@app.route('/')
def index():
    """
    default page route
    :return:
    """
    return render_template('index.html')


@app.route('/json/<path:path>')
def get_json(path):
    return send_from_directory('static/json', path)


@app.route('/graph')
def get_graph():
    results = graph.run(
        'MATCH (d:asn)<-[r:TO]-(s:asn) '
        'WHERE r.time={0} AND r.prefix="{1}" '
        'RETURN d.name as asn_a, s.name as asn_b, r.prepended as prepended '.format(timestamp, prefix)
    )

    origin_as = None
    origin = graph.run(
        'MATCH (:asn)-[:TO{{time:{0}, prefix:"{1}"}}]->(d:asn) '
        'WHERE NOT (d)-[:TO{{time:{0}, prefix:"{1}"}}]->() '
        'RETURN d.name as origin'.format(timestamp, prefix)
    )

    for ori in origin:
        origin_as = ori['origin']

    degrees = graph.run(
        'MATCH p=(d:asn{{name:"{0}"}})<-[r:TO*{{time:{1}, prefix:"{2}"}}]-(s:asn)'
        'RETURN s.name as asn, length(p) as degree'.format(origin_as, timestamp, prefix)
    )

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
    nodes[nodes.index({'title': origin_as})]['degree'] = 0

    return jsonify({'nodes':nodes, 'links': rels})


class ControlPlane(Resource):
    # TODO: add exception handler
    def get(self, version, datetime):
        print('version: {}'.format(version))
        print('datetime: {}'.format(datetime))
        msmnt = None
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