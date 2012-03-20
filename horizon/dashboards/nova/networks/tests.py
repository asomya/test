# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Cisco Systems, Inc.
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
from django import http
from django.core.urlresolvers import reverse
from mox import IsA

from horizon import api
from horizon import test
from .tables import NetworksTable
from . import forms

NETWORK_INDEX_URL = reverse('horizon:nova:networks:index')


class NetworkViewTests(test.TestCase):
    def test_index(self):
        networks = self.network_list

        self.mox.StubOutWithMock(api, 'quantum_network_list')
        api.quantum_network_list(IsA(http.HttpRequest)).\
            AndReturn(networks)
        self.mox.ReplayAll()

        res = self.client.get(NETWORK_INDEX_URL)

        self.assertTemplateUsed(res, 'nova/networks/index.html')
        resp_nets = res.context['table'].data
        self.assertEqual(len(resp_nets), len(networks))

    def test_create_network_get(self):
        res = self.client.get(reverse('horizon:nova:networks:create'))
        self.assertTemplateUsed(res, 'nova/networks/create.html')

    def test_create_network_post(self):
        self.mox.StubOutWithMock(api, 'quantum_network_create')
        api.quantum_network_create(IsA(http.HttpRequest),
                                   self.network_list[0]['name'])
        self.mox.ReplayAll()

        formData = {'name': self.network_list[0]['name'],
                    'method': forms.CreateNetwork.__name__}
        res = self.client.post(reverse('horizon:nova:networks:create'),
                               formData)
        self.assertRedirectsNoFollow(res, NETWORK_INDEX_URL)

    def test_delete_network(self):
        network = self.network_list[0]
        self.mox.StubOutWithMock(api, 'quantum_network_delete')
        api.quantum_network_delete(IsA(http.HttpRequest), network['id'])

        self.mox.ReplayAll()

        action_string = u"networks__delete__%s" % network['id']
        form_data = {"action": action_string}
        req = self.factory.post(NETWORK_INDEX_URL, form_data)
        table = NetworksTable(req, self.network_list)
        handled = table.maybe_handle()
        self.assertEqual(handled['location'], NETWORK_INDEX_URL)
