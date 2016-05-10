from anycast_dns_monitoring import app
from flask import render_template
from flask import request
from flask import jsonify
import requests
from anycast_dns_monitoring.data_processing import params
from anycast_dns_monitoring.data_processing.ripe_atlas import RipeAtlas, Version


@app.route('/')
def index():
    """
    default page route
    :return:
    """
    return render_template('index.html')


@app.route('/datetime/<int:d>', methods=['GET'])
def get_measurement(d):
    """
    get measurement result for a certain time. Use the measurement from the last 20 minutes (1200 seconds) from the
    specified time to get exactly one measurement result (measurement interval is 20 minutes)
    :param d: the specified time in UNIX timestamp format
    :return: measurement result
    """
    args = request.args
    print(args)
    msmnt = RipeAtlas(Version.ipv4)
    results = msmnt.tree_data_plane(datetime=d)

    return jsonify(result=results)


@app.route('/latest/', methods=['GET'])
def get_latest_measurement():
    """
    get the latest measurement. Should be used in the main page.
    see: https://atlas.ripe.net/docs/measurement-latest-api/
    :return:
    """
    uri = '{0}measurement-latest/{1}/'.format(params.msmnt_id, params.msmnt_id)
    results = requests.get(url=uri)
    return jsonify(results=results.json())