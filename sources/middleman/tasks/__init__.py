

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


def parse_cookies(header):
    cookies = {}
    for cookie in header.split(";"):
        cookie = cookie.strip()
        if len(cookie) != 0:
            (name,value) = cookie.split("=", 1)
            if name and value:
                cookies[name] = value
    return cookies


def broker_persona_session(config):
    try:
        driver = selenium.webdriver.Remote(
            desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
            command_executor="http://127.0.0.1:4444/wd/hub")
        return persona_login(driver, config)
    except Exception as e:
        print "Failed to broker persona session", str(e)
        return None
    finally:
        driver.quit()


def broker_fxa_session(config):
    try:
        driver = selenium.webdriver.Remote(
            desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
            command_executor="http://127.0.0.1:4444/wd/hub")
        return fxa_login(driver, config)
    except Exception as e:
        drover.save_screenshot("/tmp/failure.png")
        print "Failed to broker persona session", str(e)
        return None
    finally:
        driver.quit()


def broker_session(session_id):

    session_json = redis.get("session:%s" % session_id)
    if not session_json:
        return

    session = json.loads(session_json)
    config = session["config"]

    print "Brokering %s session for %s" % (config['method'], config['url'])

    if session["config"]["method"] == "persona":
        cookies = broker_persona_session(session["config"])
    if session["config"]["method"] == "fxa":
        cookies = broker_fxa_session(session["config"])
    else:
        session["state"] = "FAILURE"
        session["reason"] = "Unknown method '%s'" % session["config"]["method"]
        redis.set("session:%s" % session_id, json.dumps(session))
        return

    if not cookies:
        session["cookies"] = None
        session["state"] = "FAILURE"
        session["reason"] = "No cookies found"
    else:
        session["cookies"] = cookies
        session["state"] = "SUCCESS"

    print "RESULT", json.dumps(session, indent=4)
    redis.setex("session:%s" % session_id, 300, json.dumps(session))
