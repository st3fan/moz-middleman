# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def _found_window(name):
    def predicate(driver):
        try:
            driver.switch_to_window(name)
            return True
        except NoSuchWindowException:
            return False
    return predicate

def _not_found_window(name):
    def predicate(driver):
        try:
            driver.switch_to_window(name)
            return False
        except NoSuchWindowException:
            return True
    return predicate


PERSONA_WINDOW_NAME = "__persona_dialog"
PERSONA_PASSWORD_ELEMENT_ID = "authentication_password"
PERSONA_EMAIL_ELEMENT_ID = "authentication_email"


def login(driver, config):

    # Load the site
    driver.get(config["url"])

    # Wait for the page to be loaded.
    if "before_login_element_path" in config:
        e = WebDriverWait(driver, 30).until(
            _conditions.presence_of_element_located(
                (By.XPATH, config['before_login_element_path'])))

    # Start the Persona login. We have different strategies. We can
    # find and click a button or we can execute a script.
    if "login_button_xpath" in config:
        a = WebDriverWait(driver, 30).until(
            expected_conditions.visibility_of_element_located(
                (By.XPATH, config['login_button_xpath'])))
        a.click()
    elif "login_script" in config:
        driver.execute_script(config["login_script"])

    # Wait for the Persona window to appear.
    WebDriverWait(driver, timeout=30).until(_found_window(PERSONA_WINDOW_NAME))

    # Wait for the email field to become visible. Then type the email and submit.
    input = WebDriverWait(driver, 30).until(
        expected_conditions.visibility_of_element_located(
            (By.ID, PERSONA_EMAIL_ELEMENT_ID)))
    input.send_keys(config['email'])
    input.send_keys(Keys.RETURN)

    # Wait for the password field to become visible. Then type the password and submit
    input = WebDriverWait(driver, 30).until(
        expected_conditions.visibility_of_element_located(
            (By.ID, PERSONA_PASSWORD_ELEMENT_ID)))
    input.send_keys(config['password'])
    input.send_keys(Keys.RETURN)

    # Wait for the Persona window to go away. If it does not go away
    # then something went wrong and we are not logged in.
    WebDriverWait(driver, timeout=30).until(_not_found_window(PERSONA_WINDOW_NAME))

    # Switch back to the initial window
    driver.switch_to_window(driver.window_handles[0])

    # Wait for the page to reload. We wait until an element becomes
    # visible. This needs multiple strategies because some sites
    # handle this in a different way.
    a = WebDriverWait(driver, 30).until(
        expected_conditions.visibility_of_element_located(
            (By.XPATH, config["after_login_element_xpath"])))

    # Now we can grab the cookies
    return driver.get_cookies()
