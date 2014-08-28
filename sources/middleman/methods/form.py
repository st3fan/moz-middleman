# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def login(driver, config):

    # Load the site
    driver.get(config["url"])

    # Wait for the page to be loaded.
    if "before_login_element_path" in config:
        e = WebDriverWait(driver, 30).until(
            _conditions.presence_of_element_located(
                (By.XPATH, config['before_login_element_path'])))

    # Wait for the email field to become visible. Then type the email
    # and submit.
    input = WebDriverWait(driver, 30).until(
        expected_conditions.visibility_of_element_located(
            (By.XPATH, config["username_field_xpath"])))
    input.send_keys(config['username'])

    # Wait for the password field to become visible. Then type the
    # password and submit
    input = WebDriverWait(driver, 30).until(
        expected_conditions.visibility_of_element_located(
            (By.XPATH, config["password_field_xpath"])))
    input.send_keys(config['password'])

    if "login_button_xpath" in config:
        a = WebDriverWait(driver, 30).until(
            expected_conditions.visibility_of_element_located(
                (By.XPATH, config['login_button_xpath'])))
        a.click()
    elif "login_script" in config:
        driver.execute_script(config["login_script"])

    # Wait for the page to redirect back to the original site. We
    # simply wait until an element becomes visible.
    a = WebDriverWait(driver, 30).until(
        expected_conditions.visibility_of_element_located(
            (By.XPATH, config["after_login_element_xpath"])))

    # Now we can grab the cookies
    return driver.get_cookies()
