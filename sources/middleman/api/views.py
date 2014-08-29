# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

import datetime
import json
import uuid
import time

from redis import Redis, StrictRedis
from rq import Queue
from flask import Flask, jsonify, request, abort, Response, render_template, redirect, url_for

from middleman.api import app
from middleman.tasks import broker_session

redis = StrictRedis(host='localhost', port=6379, db=0)
queue = Queue(connection=Redis())


@app.template_filter('datetime')
def _jinja2_filter_datetime(unix_time):
    return datetime.datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')


@app.route("/sessions", methods=["POST"])
def post_session():
    config = request.json
    # TODO Validate config
    response = dict(config=config, id=str(uuid.uuid4()), state="WORKING", queue_time=time.time(), start_time=None,
                    finish_time=None)
    redis.setex("session:%s" % response["id"], app.config["MIDDLEMAN_SESSION_EXPIRATION"], json.dumps(response))
    queue.enqueue(broker_session, app.config["MIDDLEMAN_WEBDRIVER"], response["id"])
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

@app.route("/version", methods=["GET"])
def get_version():
    return jsonify(version="0.1")

@app.route("/", methods=["GET"])
def get_index():
    return redirect(url_for("get_status"))

@app.route("/status", methods=["GET"])
def get_status():
    status = []
    for key in redis.keys("session:*"):
        session_json = redis.get(key)
        if session_json:
            session = json.loads(session_json)
            if session["state"] == 'WORKING':
                status.append(dict(queue_time=session["queue_time"],
                                   start_time=session["start_time"],
                                   url=session["config"]["url"]))
    history = [json.loads(i) for i in redis.lrange("history", 0, 4)]
    return render_template("status.html", status=status, history=history)

@app.route("/history", methods=["GET"])
def get_history():
    history = [json.loads(i) for i in redis.lrange("history", 0, 499)]
    return render_template("history.html", history=history)
