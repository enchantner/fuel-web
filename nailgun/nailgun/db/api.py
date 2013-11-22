# -*- coding: utf-8 -*-

#    Copyright 2013 Mirantis, Inc.
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

import abc

import six

from nailgun.openstack.common.db import api as db_api


_BACKEND_MAPPING = {'sqlalchemy': 'nailgun.db.sqlalchemy.api'}
IMPL = db_api.DBAPI(backend_mapping=_BACKEND_MAPPING)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):

    @abc.abstractmethod
    def register(self, obj):
        """Register object for possible mapping with model."""

    @abc.abstractmethod
    def get_by_uid(self, obj_uid):
        """Returns object from DB by its UID"""

    @abc.abstractmethod
    def get_all(self, yield_per=100):
        """Returns all objects from db matching model."""

    @abc.abstractmethod
    def new(self, **kwargs):
        """Creates new object in DB and returns it"""

    @abc.abstractmethod
    def save(self, **kwargs):
        """Saves object in DB and returns it"""
