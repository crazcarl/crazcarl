#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from webapp2 import WSGIApplication, Route

import os
# Set useful fields
root_dir = os.path.dirname(__file__)
template_dir = os.path.join(root_dir, 'templates')

from google.appengine.ext import db


# Create the WSGI application and define route handlers\
# Temporarily route to set
app = WSGIApplication([
	Route(r'/', handler='handlers.set.SetHandler', name='blog'),
	Route(r'/set',handler='handlers.set.SetHandler',name='set'),
	Route(r'/checkset',handler='handlers.set.SetHandler',name='checkSet',handler_method='checkSet')
], debug=True)