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

Status
======

Work in progress. Everything is subject to change at this point.
