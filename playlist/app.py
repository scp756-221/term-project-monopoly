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
metrics.info('app_info', 'User process')

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


@bp.route('/<playlist_id>/add/<music_id>', methods=['PUT'])
def addmusic_playlist(playlist_id, music_id):
  headers = request.headers
  
  if 'Authorization' not in headers:
    return Response(json.dumps({"error": "missing auth"}),
            status=401,
            mimetype='application/json')
  
  payload = {"objtype": "playlist", "objkey": playlist_id}
  url = db['name'] + '/' + db['endpoint'][0]
  playlist_res = requests.get(
    url,
    params=payload,
    headers={'Authorization': headers['Authorization']})
  
  playlist_json = playlist_res.json()
  
  if (playlist_json['Count'] == 0) | (playlist_json == {}):
    return Response(json.dumps({"error": "playlist_id not find"}),
        status=401,
        mimetype='application/json')
  
  playlist = playlist_json["Items"][0]
  song_list = playlist["song_list"]
  
  new_music_res = requests.get(
      db['name'] + '/' + db['endpoint'][0],
      params={"objtype": "music", "objkey": music_id},
      headers={'Authorization': headers['Authorization']}
  )
  
  if new_music_res.json()['Count'] == 0:
    return Response(json.dumps({"error": "music_id not find"}),
      status=401,
      mimetype='application/json')
  
  if music_id in song_list:
    return Response(json.dumps({"error": "music_id already exist " + \
                  "in playlist"}),
            status=401,
            mimetype='application/json')
  
  song_list.append(music_id)
  payload = {
    "objtype": "playlist", 
    "objkey": playlist_id
  }
  url = db['name'] + '/' + db['endpoint'][3]
  response = requests.put(
    url,
    params=payload,
    json={"song_list": song_list})
  
  return (response.json())


@bp.route('/<playlist_id>/remove/<music_id>', methods=['PUT'])
def removemusic_playlist(playlist_id, music_id):
  headers = request.headers
  
  if 'Authorization' not in headers:
    return Response(json.dumps({"error": "missing auth"}),
            status=401,
            mimetype='application/json')
  
  payload = {"objtype": "playlist", "objkey": playlist_id}
  url = db['name'] + '/' + db['endpoint'][0]
  playlist_res = requests.get(
    url,
    params=payload,
    headers={'Authorization': headers['Authorization']})
  
  playlist_json = playlist_res.json()
  
  if (playlist_json['Count'] == 0) | (playlist_json == {}):
    return Response(json.dumps({"error": "playlist_id not find"}),
        status=401,
        mimetype='application/json')
  
  playlist = playlist_json["Items"][0]
  song_list = playlist["song_list"]
  
  new_music_res = requests.get(
      db['name'] + '/' + db['endpoint'][0],
      params={"objtype": "music", "objkey": music_id},
      headers={'Authorization': headers['Authorization']}
  )
  
  if new_music_res.json()['Count'] == 0:
    return Response(json.dumps({"error": "music_id not find"}),
      status=401,
      mimetype='application/json')
  
  if music_id not in song_list:
    return Response(json.dumps({"error": "music_id does not exist " + \
                  "in playlist "}),
            status=401,
            mimetype='application/json')
  
  song_list.remove(music_id)
  
  payload = {
    "objtype": "playlist", 
    "objkey": playlist_id
  }
  url = db['name'] + '/' + db['endpoint'][3]
  response = requests.put(
    url,
    params=payload,
    json={"song_list": song_list})
  
  return (response.json())


app.register_blueprint(bp, url_prefix='/api/v1/playlist/')

# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
app.register_blueprint(bp, url_prefix='/api/v1/user/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("Usage: app.py <service-port>")
        sys.exit(-1)

    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
  