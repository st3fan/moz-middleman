# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

import json
import uuid

from redis import Redis, StrictRedis
from rq import Queue
from flask import Flask, jsonify, request, abort

from middleman.api import app
from middleman.tasks import broker_session

redis = StrictRedis(host='localhost', port=6379, db=0)
queue = Queue(connection=Redis())


@app.route("/sessions", methods=["POST"])
def post_session():
    config = request.json
    session = {"id": str(uuid.uuid4()), "state":"WORKING", "config":config}
    redis.set("session:%s" % session["id"], json.dumps(session))
    result = queue.enqueue(broker_session, session["id"], config)
    return jsonify(success=True, session=session)

@app.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    session_json = redis.get("session:%s" % session_id)
    if not session_json:
        abort(404)
    session = json.loads(session_json)
    return jsonify(success=True, session=session)
