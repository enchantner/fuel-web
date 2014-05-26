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

from nailgun.api.v1.validators.cluster import AttributesValidator
from nailgun.api.v1.validators.cluster import ClusterValidator

from nailgun.api.v2.controllers.base import BaseController
from nailgun.api.v2.controllers.base import DeferredTaskController

from nailgun.objects import Cluster
from nailgun.objects import ClusterCollection

from nailgun.task.manager import ApplyChangesTaskManager
from nailgun.task.manager import StopDeploymentTaskManager
from nailgun.task.manager import ResetEnvironmentTaskManager

from nailgun import utils


class ClusterChangesController(DeferredTaskController):

    log_message = u"Trying to start deployment at environment '{env_id}'"
    log_error = u"Error during execution of deployment " \
                u"task on environment '{env_id}': {error}"
    task_manager = ApplyChangesTaskManager


class ClusterStopDeploymentController(DeferredTaskController):

    log_message = u"Trying to stop deployment on environment '{env_id}'"
    log_error = u"Error during execution of deployment " \
                u"stopping task on environment '{env_id}': {error}"
    task_manager = StopDeploymentTaskManager


class ClusterResetController(DeferredTaskController):

    log_message = u"Trying to reset environment '{env_id}'"
    log_error = u"Error during execution of resetting task " \
                u"on environment '{env_id}': {error}"
    task_manager = ResetEnvironmentTaskManager


class ClusterAttributesController(BaseController):
    """Cluster attributes handler
    """

    fields = (
        "editable",
    )

    validator = AttributesValidator

    @pecan.expose(template='json:', content_type='application/json')
    def get_all(self, cluster_id):
        """:returns: JSONized Cluster attributes.
        :http: * 200 (OK)
               * 404 (cluster not found in db)
               * 500 (cluster has no attributes)
        """
        cluster = self.get_object_or_404(Cluster, cluster_id)
        if not cluster.attributes:
            raise self.http(500, "No attributes found!")

        return {
            "editable": cluster.attributes.editable
        }

    @pecan.expose(template='json:', content_type='application/json')
    def put_all(self, cluster_id):
        """:returns: JSONized Cluster attributes.
        :http: * 200 (OK)
               * 400 (wrong attributes data specified)
               * 404 (cluster not found in db)
               * 500 (cluster has no attributes)
        """
        cluster = self.get_object_or_404(Cluster, cluster_id)
        if not cluster.attributes:
            raise self.http(500, "No attributes found!")

        if cluster.is_locked:
            raise self.http(403, "Environment attributes can't be changed "
                                 "after, or in deploy.")

        data = self.checked_data()

        for key, value in data.iteritems():
            setattr(cluster.attributes, key, value)

        objects.Cluster.add_pending_changes(cluster, "attributes")
        return {"editable": cluster.attributes.editable}

    @pecan.expose(template='json:', content_type='application/json')
    def patch_all(self, cluster_id):
        """:returns: JSONized Cluster attributes.
        :http: * 200 (OK)
               * 400 (wrong attributes data specified)
               * 404 (cluster not found in db)
               * 500 (cluster has no attributes)
        """
        cluster = self.get_object_or_404(Cluster, cluster_id)

        if not cluster.attributes:
            raise self.http(500, "No attributes found!")

        if cluster.is_locked:
            raise self.http(403, "Environment attributes can't be changed "
                                 "after, or in deploy.")

        data = self.checked_data()

        cluster.attributes.editable = utils.dict_merge(
            cluster.attributes.editable, data['editable'])

        objects.Cluster.add_pending_changes(cluster, "attributes")
        return {"editable": cluster.attributes.editable}


class ClusterController(BaseController):
    """Cluster single handler
    """

    changes = ClusterChangesController()
    stop_deployment = ClusterStopDeploymentController()
    reset = ClusterResetController()
    attributes = ClusterAttributesController()

    single = Cluster
    collection = ClusterCollection
    validator = ClusterValidator

    @pecan.expose(template='json:', content_type='application/json')
    def delete_one(self, obj_id):
        """:returns: {}
        :http: * 202 (cluster deletion process launched)
               * 400 (failed to execute cluster deletion process)
               * 404 (cluster not found in db)
        """
        cluster = self.get_object_or_404(self.single.model, obj_id)
        task_manager = ClusterDeletionManager(cluster_id=cluster.id)
        try:
            logger.debug('Trying to execute cluster deletion task')
            task_manager.execute()
        except Exception as e:
            logger.warn('Error while execution '
                        'cluster deletion task: %s' % str(e))
            logger.warn(traceback.format_exc())
            raise self.http(400, unicode(e))

        raise self.http(202, u'{}')
