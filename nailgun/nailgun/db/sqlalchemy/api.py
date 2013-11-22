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

from nailgun.db import api
from nailgun.db import db_str
from nailgun.db.sqlalchemy import models
from nailgun.logger import logger
from nailgun.openstack.common.db.sqlalchemy import session as db_session
from nailgun.settings import settings

from oslo.config import cfg


get_engine = db_session.get_engine
get_session = db_session.get_session

CONF = cfg.CONF
CONF.set_override('connection', db_str, 'database')


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


class Connection(api.Connection):

    def register(self, name):
        self.model = getattr(models, name)
        if not self.model:
            logger.debug(
                u"Failed to register model '{0}' "
                u"- no corresponding DB model.".format(name)
            )
        return self

    def get_by_uid(self, obj_uid):
        return model_query(self.model).get(obj_uid)

    def get_all(self, yield_per=100):
        return model_query(self.model).yield_per(yield_per)

    def new(self, **kwargs):
        session = get_session()
        new_obj = self.model(**kwargs)
        session.add(new_obj)
        return new_obj

    def save(self, **kwargs):
        session = get_session()
        new_obj = self.model(**kwargs)
        session.add(new_obj)
        return new_obj
