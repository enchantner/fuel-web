# -*- coding: utf-8 -*-

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

import mock

from fuel_upgrade.tests.base import BaseTestCase
from fuel_upgrade.upgrade import Upgrade


class TestUpgrade(BaseTestCase):

    def default_args(self, **kwargs):
        default = {
            'update_path': '/tmp/src_file',
            'working_dir': '/tmp/dst_file',
            'upgrade_engine': mock.Mock(),
            'disable_rollback': False}

        default.update(kwargs)
        return default

    def test_run_rollback_in_case_of_errors(self):
        engine_mock = mock.Mock()
        engine_mock.upgrade.side_effect = Exception('Upgrade failed')
        upgrader = Upgrade(**self.default_args(upgrade_engine=engine_mock))
        upgrader.run()

        engine_mock.backup.assert_called_once_with()
        engine_mock.upgrade.assert_called_once_with()
        engine_mock.rollback.assert_called_once_with()

    def test_does_not_run_rollback_if_disabled(self):
        engine_mock = mock.Mock()
        engine_mock.upgrade.side_effect = Exception('Upgrade failed')
        upgrader = Upgrade(**self.default_args(
            upgrade_engine=engine_mock,
            disable_rollback=True))
        upgrader.run()

        engine_mock.backup.assert_called_once_with()
        engine_mock.upgrade.assert_called_once_with()
        self.method_was_not_called(engine_mock.rollback.call_count)

    def test_upgrade_succed(self):
        engine_mock = mock.Mock()
        upgrader = Upgrade(**self.default_args(upgrade_engine=engine_mock))
        upgrader.run()

        engine_mock.backup.assert_called_once_with()
        engine_mock.upgrade.assert_called_once_with()
        self.method_was_not_called(engine_mock.rollback.call_count)
