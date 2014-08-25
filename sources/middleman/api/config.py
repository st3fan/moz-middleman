# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

class DefaultConfig:

    DEBUG = True
    SESSION_COOKIE_NAME = "middleman-dev"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = "development-key-please-change-me-cheese-nom-nom-nom"
    JSONIFY_PRETTYPRINT_REGULAR = True
