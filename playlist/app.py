# Standard library modules
import logging
import sys
import time

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

import jwt

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json

# The application

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Playlist process')

bp = Blueprint('app', __name__)

db = {
    "name": "http://cmpt756db:30002/api/v1/datastore",
    "endpoint": [
        "read",
        "write",
        "delete",
        "update"
    ]
}


@bp.route('/health')
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")


@bp.route('/', methods=['GET'])
def list_all():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    # list all songs here
    return {}


def get_song(headers, music_id):
    url = db['name'] + '/' + db['endpoint'][0]
    payload = {"objtype": "music", "objkey": music_id}
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    return response.json()


@bp.route('/', methods=['POST'])
def create_playlist():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        playlist_name = content['playlist_name']
        song_list = content['song_list'].strip().split(",")
    except Exception:
        return json.dumps({"message": "error reading arguments"})
    
    for music_id in song_list:
        response = get_song(headers, music_id)
        if response['Count'] == 0:
            return Response(json.dumps({"error": "music_id not find"}),
                status=444,
                mimetype='application/json')

    url = db['name'] + '/' + db['endpoint'][1]
    payload = {"objtype": "playlist", "song_list": song_list}
    response = requests.post(
        url,
        json=payload,
        headers={'Authorization': headers['Authorization']})
    return (response.json())


@bp.route('/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    url = db['name'] + '/' + db['endpoint'][2]
    response = requests.delete(
        url,
        params={"objtype": "playlist", "objkey": playlist_id},
        headers={'Authorization': headers['Authorization']})
    return (response.json())


@bp.route('/<playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    pass


@bp.route('/<playlist_id>/add', methods=['POST'])
def add_song(playlist_id):
    pass


@bp.route('/<playlist_id>/delete', methods=['POST'])
def delete_song(playlist_id):
    pass


app.register_blueprint(bp, url_prefix='/api/v1/playlist/')

# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
