from anycast_dns_monitoring import app
from flask import render_template
from flask import jsonify
import requests
from anycast_dns_monitoring.data_processing.helpers import get_probe_list
from anycast_dns_monitoring.data_processing.traceroute_processor import TracerouteProcessor

measurement_id = '2048556'
base_uri = 'https://atlas.ripe.net/api/v1/'


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
    uri = '{0}measurement/{1}/result/?start={2}&stop={3}'.format(base_uri, measurement_id, int(d) - 1200, d)
    print(uri)
    results = requests.get(url=uri).json()

    result = TracerouteProcessor(results)

    return jsonify(result=results)


@app.route('/latest/', methods=['GET'])
def get_latest_measurement():
    """
    get the latest measurement. Should be used in the main page.
    see: https://atlas.ripe.net/docs/measurement-latest-api/
    :return:
    """
    uri = '{0}measurement-latest/{1}/'.format(base_uri, measurement_id)
    results = requests.get(url=uri)
    return jsonify(results=results.json())