# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import json
import time
import subprocess
import threading
import Queue

from redis import StrictRedis
import selenium
import selenium.common.exceptions

from middleman.methods.persona import login as persona_login
from middleman.methods.fxa import login as fxa_login


redis = StrictRedis(host='localhost', port=6379, db=0)


def _broker_persona_session(driver, config):
    return persona_login(driver, config)

def _broker_fxa_session(driver, config):
    return fxa_login(driver, config)


SESSION_BROKERS = {
    "persona": _broker_persona_session,
    "fxa": _broker_fxa_session
}


def _webdriver_from_config(webdriver_config):
    if webdriver_config["type"] == "local":
        return selenium.webdriver.Firefox(
            firefox_binary=webdriver_config.get("path"))
    if webdriver_config["type"] == "remote":
        return selenium.webdriver.Remote(
            desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
            command_executor=webdriver_config.get("url", "http://127.0.0.1:4444/wd/hub"))


def broker_session(webdriver_config, session_id):

    session_json = redis.get("session:%s" % session_id)
    if not session_json:
        return

    session = json.loads(session_json)
    config = session["config"]

    session_broker = SESSION_BROKERS.get(config["method"])
    if session_broker is None:
        session["state"] = "FAILURE"
        session["reason"] = "Unknown method '%s'" % session["config"]["method"]
        redis.set("session:%s" % session_id, json.dumps(session))
        return

    # Create the driver

    driver = _webdriver_from_config(webdriver_config)
    if not driver:
        session["state"] = "FAILURE"
        session["reason"] = "Could not create WebDriver from config '%s'" % str(webdriver_config)
        redis.set("session:%s" % session_id, json.dumps(session))
        return

    # Run the script against the driver

    start_time = time.time()

    try:
        cookies = session_broker(driver, config)
        if not cookies:
            session["cookies"] = None
            session["state"] = "FAILURE"
            session["reason"] = "No cookies found"
        else:
            for cookie in cookies:
                if "hCode" in cookie:
                    del cookie["hCode"]
                if "class" in cookie:
                    del cookie["class"]
            session["cookies"] = cookies
            session["state"] = "SUCCESS"
    except selenium.common.exceptions.TimeoutException as e:
        session["state"] = "TIMEOUT"
        try:
            screenshot_png = driver.get_screenshot_as_png()
            redis.setex("screenshot:%s" % session_id, 300, screenshot_png)
            session["screenshot"] = "http://127.0.0.1:8080/screenshots/%s" % session_id
        except:
            pass
    except Exception as e:
        session["state"] = "EXCEPTION"
        session["reason"] = str(e)
    finally:
        if driver:
            driver.quit()

    session["duration"] = time.time() - start_time

    redis.setex("session:%s" % session_id, 300, json.dumps(session))
