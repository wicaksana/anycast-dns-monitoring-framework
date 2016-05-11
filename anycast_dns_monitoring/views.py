from anycast_dns_monitoring import app, api
from flask import render_template
from flask import request
from flask import jsonify
from flask_restful import Resource
import requests
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.ris import Ris
from anycast_dns_monitoring.data_processing.ripe_atlas import RipeAtlas, Version


@app.route('/')
def index():
    """
    default page route
    :return:
    """
    return render_template('index.html')


# @app.route('/datetime/<int:d>', methods=['GET'])
# def get_measurement(d):
#     """
#     get measurement result for a certain time. Use the measurement from the last 20 minutes (1200 seconds) from the
#     specified time to get exactly one measurement result (measurement interval is 20 minutes)
#     :param d: the specified time in UNIX timestamp format
#     :return: measurement result
#     """
#     args = request.args
#     print(args)
#     msmnt = RipeAtlas(Version.ipv4)
#     results = msmnt.tree_data_plane(datetime=d)
#
#     return jsonify(result=results)
#
#
# @app.route('/latest/', methods=['GET'])
# def get_latest_measurement():
#     """
#     get the latest measurement. Should be used in the main page.
#     see: https://atlas.ripe.net/docs/measurement-latest-api/
#     :return:
#     """
#     uri = '{0}measurement-latest/{1}/'.format(params.atlas_uri, params.msmnt_id)
#     print(uri)
#     results = requests.get(url=uri)
#     return jsonify(results=results.json())


class ControlPlane(Resource):
    # TODO: add exception handler
    def get(self, version, datetime):
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