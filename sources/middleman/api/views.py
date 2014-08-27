# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

import json
import uuid

from redis import Redis, StrictRedis
from rq import Queue
from flask import Flask, jsonify, request, abort, Response

from middleman.api import app
from middleman.tasks import broker_session

redis = StrictRedis(host='localhost', port=6379, db=0)
queue = Queue(connection=Redis())


@app.route("/sessions", methods=["POST"])
def post_session():
    config = request.json
    # TODO Validate config
    response = dict(config=config, id=str(uuid.uuid4()), state="WORKING")
    redis.setex("session:%s" % response["id"], app.config["MIDDLEMAN_SESSION_EXPIRATION"], json.dumps(response))
    queue.enqueue(broker_session, response["id"])
    del response["config"]
    return jsonify(response)

@app.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    session_json = redis.get("session:%s" % session_id)
    if not session_json:
        abort(404)
    session = json.loads(session_json)
    del session["config"]
    return jsonify(session)

@app.route("/screenshots/<screenshot_id>", methods=["GET"])
def get_screenshot(screenshot_id):
    screenshot_png = redis.get("screenshot:%s" % screenshot_id)
    if not screenshot_png:
        abort(404)
    return Response(screenshot_png, mimetype="image/png")
