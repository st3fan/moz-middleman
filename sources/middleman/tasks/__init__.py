

import json
import time
import subprocess
import threading
import Queue

from redis import StrictRedis
import selenium

from middleman.methods.persona import login as persona_login
from middleman.methods.fxa import login as fxa_login


redis = StrictRedis(host='localhost', port=6379, db=0)


def _broker_persona_session(config):
    try:
        driver = selenium.webdriver.Remote(
            desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
            command_executor="http://127.0.0.1:4444/wd/hub")
        return persona_login(driver, config)
    finally:
        driver.quit()


def _broker_fxa_session(config):
    try:
        driver = selenium.webdriver.Remote(
            desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
            command_executor="http://127.0.0.1:4444/wd/hub")
        return fxa_login(driver, config)
    finally:
        driver.quit()


SESSION_BROKERS = {
    "persona": _broker_persona_session,
    "fxa": _broker_fxa_session
}


def broker_session(session_id):

    session_json = redis.get("session:%s" % session_id)
    if not session_json:
        return

    session = json.loads(session_json)
    config = session["config"]

    print "Brokering %s session for %s" % (config['method'], config['url'])

    session_broker = SESSION_BROKERS.get(config["method"])
    if session_broker is None:
        session["state"] = "FAILURE"
        session["reason"] = "Unknown method '%s'" % session["config"]["method"]
        redis.set("session:%s" % session_id, json.dumps(session))
        return

    start_time = time.time()

    try:
        cookies = session_broker(config)
        if not cookies:
            session["cookies"] = None
            session["state"] = "FAILURE"
            session["reason"] = "No cookies found"
        else:
            for cookie in cookies:
                del cookie["hCode"]
                del cookie["class"]
            session["cookies"] = cookies
            session["state"] = "SUCCESS"
    except Exception as e:
        session["state"] = "EXCEPTION"
        session["reason"] = str(e)

    session["duration"] = time.time() - start_time

    redis.setex("session:%s" % session_id, 300, json.dumps(session))
