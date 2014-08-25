

import os
import unittest
import selenium
import middleman.methods.fxa


class FirefoxAccountsTestCase(unittest.TestCase):

    def setUp(self):
        if os.getenv('FXA_EMAIL') is None or os.getenv('FXA_PASSWORD') is None:
            raise Exception("PersonaTestCase needs FXA_EMAIL and FXA_PASSWORD to be set")
        self.email = os.getenv('FXA_EMAIL')
        self.password = os.getenv('FXA_PASSWORD')
        self.driver = selenium.webdriver.Remote(desired_capabilities=selenium.webdriver.DesiredCapabilities.FIREFOX,
                                                command_executor="http://127.0.0.1:4444/wd/hub")

    def test_find(self):
        find_config = {
            "url": "https://find.firefox.com",
            "email": self.email,
            "password": self.password,
            "login_button_xpath": "//a[@href='/signin/']",
            "after_login_element_xpath": "//a[@href='/signout/']"
        }
        cookies = middleman.methods.fxa.login(self.driver, find_config)
        self.assertTrue(len(cookies) > 0)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
