#    Copyright 2014 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pecan
from webob.exc import status_map

from nailgun.api.v2.controllers.base import BaseController

from nailgun.api.v2.controllers.release import ReleaseController
from nailgun.api.v2.controllers.cluster import ClusterController


class APIController(BaseController):

    releases = ReleaseController()
    clusters = ClusterController()


class RootController(object):

    api = APIController()

    @pecan.expose('jinja:index.html')
    def index(self):
        return dict()
