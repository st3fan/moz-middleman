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
from middleman.methods.form import login as form_login


redis = StrictRedis(host='localhost', port=6379, db=0)


SESSION_BROKERS = {
    "persona": persona_login,
    "fxa": fxa_login,
    "form": form_login,
}


def _store_history_item_for_session(session):
    history_item = dict(queue_time=session["queue_time"],
                        start_time=session["start_time"],
                        finish_time=session["finish_time"],
                        url=session["config"]["url"],
                        state=session["state"])
    redis.lpush("history", json.dumps(history_item))


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

    session["start_time"] = time.time()
    redis.set("session:%s" % session_id, json.dumps(session))

    session_broker = SESSION_BROKERS.get(config["method"])
    if session_broker is None:
        session["state"] = "FAILURE"
        session["reason"] = "Unknown method '%s'" % session["config"]["method"]
        session["finish_time"] = time.time()
        redis.set("session:%s" % session_id, json.dumps(session))
        _store_history_item_for_session(session)
        return

    # Create the driver

    driver = _webdriver_from_config(webdriver_config)
    if not driver:
        session["state"] = "FAILURE"
        session["reason"] = "Could not create WebDriver from config '%s'" % str(webdriver_config)
        session["finish_time"] = time.time()
        redis.set("session:%s" % session_id, json.dumps(session))
        _store_history_item_for_session(session)
        return

    # Run the script against the driver

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
            redis.setex("screenshot:%s" % session_id, 24*60*60, screenshot_png)
            session["screenshot"] = session_id
        except:
            pass
    except Exception as e:
        session["state"] = "EXCEPTION"
        session["reason"] = str(e)
    finally:
        if driver:
            driver.quit()

    session["finish_time"] = time.time()
    redis.setex("session:%s" % session_id, 300, json.dumps(session))
    _store_history_item_for_session(session)
