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

from collections import defaultdict
from itertools import imap

from nailgun.api.serializers.base import BasicSerializer


class NailgunObject(defaultdict):

    serializer = BasicSerializer
    schema = None
    dbapi = None

    @classmethod
    def render(cls, obj):
        fields = cls.schema["properties"].keys()
        return cls.serializer.serialize(obj, fields)

    @classmethod
    def get_by_id(cls, obj_uid):
        return cls.render(
            cls.dbapi.get_by_id(obj_uid)
        )

    @classmethod
    def get_all(cls):
        return imap(
            cls.render,
            cls.dbapi.get_all()
        )

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            self[key] = value

    def save(self):
        return self.render(
            self.dbapi.save(**self)
        )
