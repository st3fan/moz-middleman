Introduction
============

Mozilla Middleman is a web service that can login to sites and return you the session cookies that the site sets after a succesful login. It is typically used in automation projects.

Middleman currently supports the following authentication methods:

 * Mozilla Persona
 * Firefox Accounts
 * Form Based Authentication

The project relies on a Selenium server to control a Firefox browser instance.

API
===

Example Request Flow
====================

To request a session to be brokered, post a configuration that describes how to login. Note that this includes a plaintext username and password. Although the server never exposes the credentials after the initial submission of the configuration, it is best to use credentials specifically for testing.

```
POST /sessions
Content-Type: application/json

{
  "url": "https://badges.mozilla.org",
  "method": "persona",
  "email": "someone@some.domain",
  "password": "SomethingVerySecret",
  "login_button_xpath": "//a[@class='browserid-signin']",
  "after_login_element_xpath": "//a[@class='signed-in-user']"
}
```

The response will contain an `id` that you can use to poll for the results. It can take a little while before you get a result back.

```
{
  "id": "d965bfd9-0bb7-407a-a787-bf95e6c38fd8",
  "state": "WORKING"
}
```

Polling is a simple `GET` that includes the session `id`.

```
GET /sessions/d965bfd9-0bb7-407a-a787-bf95e6c38fd8
```

And once the broker is ready, the session state will change to `FINISHED` and a `cookies` field will contain a list of all the cookies set by the site after logging in.

```
{
  "result": {
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
  },
  "id": "d965bfd9-0bb7-407a-a787-bf95e6c38fd8",
  "state": "FINISHED"
}
```

Other possible values for `state` are:

 * `TIMEOUT`
 * `FAILURE`
 * `EXCEPTION`

Status
======

Things are in good shape.
