Introduction
============

Mozilla Middleman is a web service that can login to sites and return
you the session cookies that the site sets after a succesful login.

It is typically used in automation projects or integrated into tools
that otherwise cannot deal with a specific authenticagion method.

For example, at Mozilla we have many sites that require a Persona
login. Persona is a complicated interaction between a browser and a
set of servers. Because Persona needs a full browser runtime, it is
difficult to automate it with just plain HTTP requests.

This is where Middleman comes in; you only have to tell Middleman what
button to push to start the Persona authentication flow and optionally
what element to check for to recognize a succesful login.

Supported Authentication Methods
================================

Middleman currently supports the following authentication methods:

 * Mozilla Persona
 * Firefox Accounts
 * Form Based Authentication

It is relatively easy to add additional methods. If you for example are interested in a Facebook or Twitter login flow, please file a bug.

HTTP API
========

Middleman has a simple HTTP based API. In short: you post a
configuration to Middleman, which returns a session id. You can then
periodcially poll Middleman using that session id. When the session
has finished it will return the session cookies obtained.

Example Request Flow
====================

To request a session to be brokered, post a configuration that
describes how to login. Note that this includes a plaintext username
and password. It is best to use credentials specifically for testing.

```
POST /sessions
Content-Type: application/json

{
  "config": {
        "url": "https://badges.mozilla.org",
        "method": "persona",
        "email": "someone@some.domain",
        "password": "SomethingVerySecret",
        "login_button_xpath": "//a[@class='browserid-signin']",
        "after_login_element_xpath": "//a[@class='signed-in-user']"
  }
}
```

The response will contain an `id` that you can use to poll for the results. It can take a little while before you get a result back.

```
{
  "session": {
    "config": {
      "after_login_element_xpath": "//a[@class='signed-in-user']",
      "email": "someone@some.domain",
      "login_button_xpath": "//a[@class='browserid-signin']",
      "method": "persona",
      "password": "SomethingVerySecret",
      "url": "https://badges.mozilla.org"
    },
    "id": "d965bfd9-0bb7-407a-a787-bf95e6c38fd8",
    "state": "WORKING"
  },
  "success": true
}
```

Polling is a simple `GET` that includes the session `id`.

```
GET /sessions/d965bfd9-0bb7-407a-a787-bf95e6c38fd8
```

And once the broker is ready, the session state will change to `FINISHED` and a `cookies` field will contain a list of all the cookies set by the site after logging in.

```
{
  "session": {
    "config": {
      "after_login_element_xpath": "//a[@class='signed-in-user']",
      "email": "someone@some.domain",
      "login_button_xpath": "//a[@class='browserid-signin']",
      "method": "persona",
      "password": "SomethingVerySecret",
      "url": "https://badges.mozilla.org"
    },
    "cookies": [
      {
        "domain": "badges.mozilla.org",
        "expiry": 1408934487,
        "name": "multidb_pin_writes",
        "path": "/",
        "secure": false,
        "value": "y"
      },
      {
        "domain": "badges.mozilla.org",
        "expiry": 1408941672,
        "name": "anoncsrf",
        "path": "/",
        "secure": true,
        "value": "dekdlkejdlkejlkdjelkjdekljl"
      },
      {
        "domain": ".mozilla.org",
        "expiry": 1472006475,
        "name": "_ga",
        "path": "/",
        "secure": false,
        "value": "GA1.2.1234567890.1234567890"
      },
      {
        "domain": "badges.mozilla.org",
        "expiry": 1410144074,
        "name": "sessionid",
        "path": "/",
        "secure": true,
        "value": "dkjelkdjekljdlkejdkljekldjekljdlkej"
      }
    ],
    "id": "d965bfd9-0bb7-407a-a787-bf95e6c38fd8",
    "state": "FINISHED"
  },
  "success": true
}
```

Session Configuration Options
=============================

Persona
-------

The following options are accepted for a Persona login:

Option                     | Description
-------------------------- | ------------------------
method                     | Always set to "persona"
url                        | The URL of the original website
email                      | The email address of the Persona account
password                   | The password of the Persona account
before_login_element_xpath | The XPath expression of the element on the original site to wait for before
login_button_xpath         | The XPath expression of the element to click to start the login process
login_script               | The javascript expression to execute in the browser to start the login process
after_login_element_xpath  | The XPath expression of the element on the original site to wait for after the Persona login process

Firefox Accounts
----------------

The following options are accepted for a Firefox Accounts login:

Option                     | Description
-------------------------- | -----------------------
method                     | Always set to "fxa"
url                        | The URL of the original website
email                      | The email address of the Firefox Accounts account
password                   | The password of the Firefox Accounts account
before_login_element_xpath | The XPath expression of the element on the original site to wait for before
login_button_xpath         | The XPath expression of the element to click to start the login process
login_script               | The javascript expression to execute in the browser to start the login process
after_login_element_xpath  | The XPath expression of the element on the original site to wait for after the Persona login process

Generic Form Based
------------------

The following options are accepted for a Form Based login:

Option                     | Description
-------------------------- | -----------------------
method                     | Always set to "fxa"
url                        | The URL of the original website
username                   | The username to login with (can be anything, including an email)
password                   | The password to login with
before_login_element_xpath | The XPath expression of the element on the original site to wait for before
username_field_xpath       | The XPath expression of the username field
password_field_xpath       | The XPath expression of the password field
login_button_xpath         | The XPath expression of the element to click to start the login process
login_script               | The javascript expression to execute in the browser to start the login process
after_login_element_xpath  | The XPath expression of the element on the original site to wait for after the Persona login process

