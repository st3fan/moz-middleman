

import os
import unittest
import selenium
import middleman.methods.persona as persona


class PersonaTestCase(unittest.TestCase):

    def setUp(self):
        if os.getenv('PERSONA_EMAIL') is None or os.getenv('PERSONA_PASSWORD') is None:
            raise Exception("PersonaTestCase needs PERSONA_EMAIL and PERSONA_PASSWORD to be set")
        self.email = os.getenv('PERSONA_EMAIL')
        self.password = os.getenv('PERSONA_PASSWORD')
        self.driver = selenium.webdriver.Remote(desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
                                                command_executor="http://127.0.0.1:4444/wd/hub")

    def test_mozillians(self):
        mozillians_config = {
            "url": "https://mozillians.org",
            "email": self.email,
            "password": self.password,
            "login_button_xpath": "//a[@id='nav-login']",
            "after_login_element_xpath": "//span[@class='username']"
        }
        cookies = persona.login(self.driver, mozillians_config)
        self.assertTrue(len(cookies) > 0)

    def test_bugzilla(self):
        bugzilla_config = {
            "url": "https://bugzilla.mozilla.org",
            "email": self.email,
            "password": self.password,
            "before_login_element_xpath": "//a[@id='login_link_top']",
            "login_script": "persona_sign_in()",
            "after_login_element_xpath": "//td[@id='moz_login']"
        }
        cookies = persona.login(self.driver, bugzilla_config)
        self.assertTrue(len(cookies) > 0)

    def test_marketplace(self):
        marketplace_config = {
            "url": "https://marketplace.firefox.com/settings",
            "email": self.email,
            "password": self.password,
            "login_button_xpath": "//a[@class='button persona logged-out']",
            "after_login_element_xpath": "//a[@href='/settings']"
        }
        cookies = persona.login(self.driver, marketplace_config)
        self.assertTrue(len(cookies) > 0)

    def test_mdn(self):
        config = {
            "url": "https://developer.mozilla.org",
            "email": self.email,
            "password": self.password,
            "before_login_element_xpath": "//div[@class='oauth-login-container']",
            "login_script": "allauth.persona.login('/en\u002DUS/', 'login')",
            "after_login_element_xpath": "//div[@class='user-state']"
        }
        cookies = persona.login(self.driver, config)
        self.assertTrue(len(cookies) > 0)

    def test_reps(self):
        config = {
            "url": "https://reps.mozilla.org",
            "email": self.email,
            "password": self.password,
            "login_button_xpath": "//a[@class='browserid-login']",
            "after_login_element_xpath": "//a[@class='browserid-logout']"
        }
        cookies = persona.login(self.driver, config)
        self.assertTrue(len(cookies) > 0)

    def test_affiliates(self):
        config = {
            "url": "https://affiliates.mozilla.org",
            "email": self.email,
            "password": self.password,
            "login_button_xpath": "//a[@class='browserid-login persona-button']",
            "after_login_element_xpath": "//a[@aria-owns='nav-user-submenu']"
        }
        cookies = persona.login(self.driver, config)
        self.assertTrue(len(cookies) > 0)

    def test_ask(self):
        config = {
            "url": "https://ask.mozilla.org/account/signin/?next=/",
            "email": self.email,
            "password": self.password,
            "login_button_xpath": "//input[@class='mozilla-persona']",
            "after_login_element_xpath": "//div[@id='userToolsNav']"
        }
        cookies = persona.login(self.driver, config)
        self.assertTrue(len(cookies) > 0)

    def test_badges(self):
        config = {
            "url": "https://badges.mozilla.org",
            "email": self.email,
            "password": self.password,
            "login_button_xpath": "//a[@class='browserid-signin']",
            "after_login_element_xpath": "//a[@class='signed-in-user']"
        }
        cookies = persona.login(self.driver, config)
        self.assertTrue(len(cookies) > 0)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
