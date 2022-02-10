#!/usr/bin/env python3

# Copyright 2021 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import sys

sys.path.append("lib")  # noqa
sys.path.append("src")  # noqa

import charm
import advanced_sunbeam_openstack.test_utils as test_utils


class _CinderWallabyOperatorCharm(charm.CinderWallabyOperatorCharm):
    def __init__(self, framework):
        self.seen_events = []
        self.render_calls = []
        super().__init__(framework)

    def _log_event(self, event):
        self.seen_events.append(type(event).__name__)

    def renderer(
        self,
        containers,
        container_configs,
        template_dir,
        openstack_release,
        adapters,
    ):
        self.render_calls.append(
            (
                containers,
                container_configs,
                template_dir,
                openstack_release,
                adapters,
            )
        )

    def configure_charm(self, event):
        super().configure_charm(event)
        self._log_event(event)


class TestCinderOperatorCharm(test_utils.CharmTestCase):

    PATCHES = []

    @mock.patch(
        "charms.observability_libs.v0.kubernetes_service_patch."
        "KubernetesServicePatch"
    )
    def setUp(self, mock_patch):
        self.container_calls = {
            "push": {},
            "pull": [],
            "exec": [],
            "remove_path": [],
        }
        super().setUp(charm, self.PATCHES)
        self.harness = test_utils.get_harness(
            _CinderWallabyOperatorCharm, container_calls=self.container_calls
        )
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.maxDiff = None

    def set_pebble_ready(self) -> None:
        # Mark both containers as ready for use
        self.harness.container_pebble_ready("cinder-api")
        self.harness.container_pebble_ready("cinder-scheduler")

    def add_storage_backend_relation(self) -> None:
        self.storage_rel_id = self.harness.add_relation(
            "storage-backend", "cinder-ceph"
        )
        self.harness.add_relation_unit(self.storage_rel_id, "cinder-ceph/0")
        self.harness.add_relation_unit(self.storage_rel_id, "cinder-ceph/1")
        self.harness.update_relation_data(
            self.storage_rel_id,
            "cinder-ceph/0",
            {"ingress-address": "10.0.0.1"},
        )
        self.harness.update_relation_data(
            self.storage_rel_id,
            "cinder-ceph/1",
            {"ingress-address": "10.0.0.2"},
        )

    def test_application_ready(self):
        """Test when charm is ready configs are written correctly."""
        self.harness.set_leader()
        self.set_pebble_ready()
        # Setup Identity, AMQP and DB relations for API services
        self.add_storage_backend_relation()
        test_utils.add_api_relations(self.harness)
        # TODO validate config file content as well?
        # TODO check which files are written to each container?
        self.assertEqual(
            list(self.container_calls["push"].keys()),
            [
                "/etc/cinder/cinder.conf",
                "/etc/apache2/sites-available/wsgi-cinder-api.conf",
            ],
        )
        self.assertEqual(
            self.container_calls["exec"],
            [
                ["a2ensite", "wsgi-cinder-api"],
                [
                    "sudo",
                    "-u",
                    "cinder",
                    "cinder-manage",
                    "--config-dir",
                    "/etc/cinder",
                    "db",
                    "sync",
                ],
            ],
        )
