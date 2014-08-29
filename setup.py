#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

from setuptools import setup

install_requires = [
    'Flask',
    'rq',
    'redis',
    'selenium',
    'gunicorn==19.1.1',
]

setup(name="middleman",
      version="0.3",
      description="Middleman",
      url="https://github.com/st3fan/moz-middleman",
      author="Stefan Arentz",
      author_email="sarentz@mozilla.com",
      install_requires = install_requires,
      packages=["middleman", "middleman.methods", "middleman.tasks", "middleman.api", "middleman.api.static", "middlema
n.api.templates"],
      package_dir={'': 'sources'},
      include_package_data=True,
      scripts=["scripts/middleman-api", "scripts/middleman-worker", "scripts/middleman-client"])
