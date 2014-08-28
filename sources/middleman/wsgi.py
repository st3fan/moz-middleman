# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Setup the application for production

MIDDLEMAN_CONFIG = "/etc/middleman/middleman-api.cfg.py"

from middleman.api import app, configure_app
application = configure_app(app, MIDDLEMAN_CONFIG)
