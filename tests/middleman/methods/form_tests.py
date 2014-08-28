# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import os
import unittest
import selenium
import middleman.methods.form


class FormTestCase(unittest.TestCase):

    def setUp(self):
        if os.getenv('FORM_USERNAME') is None or os.getenv('FORM_PASSWORD') is None:
            raise Exception("FormTestCase needs FORM_USERNAME and FORM_PASSWORD to be set")
        self.email = os.getenv('FORM_USERNAME')
        self.password = os.getenv('FORM_PASSWORD')
        self.driver = selenium.webdriver.Remote(desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
                                                command_executor="http://127.0.0.1:4444/wd/hub")

    def test_wiki(self):
        config = {
            "url": "https://wiki.mozilla.org/index.php?title=Special:UserLogin",
            "username": self.email,
            "password": self.password,
            "username_field_xpath": "//input[@id='wpName1']",
            "password_field_xpath": "//input[@id='wpPassword1']",
            "login_button_xpath": "//input[@id='wpLoginAttempt']",
            "after_login_element_xpath": "//a[@title='Log out']"
        }
        cookies = middleman.methods.form.login(self.driver, config)
        self.assertTrue(len(cookies) > 0)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
