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
from .tables import PortsTable
from . import forms


class PortViewTests(test.TestCase):
    def test_ports(self):
        network = self.network_list[0]
        ports = self.port_list
        self.mox.StubOutWithMock(api, 'quantum_port_list')
        api.quantum_port_list(IsA(http.HttpRequest), network['id']).\
            AndReturn(ports)

        self.mox.ReplayAll()
        res = self.client.get(
            reverse('horizon:nova:networks:ports:ports',
                    kwargs={'network_id': network['id']}))

        self.assertTemplateUsed(res, 'nova/networks/ports/index.html')
        resp_ports = res.context['table'].data
        self.assertEqual(len(resp_ports), len(ports))

    def test_ports_create_get(self):
        network = self.network_list[0]
        port = self.port_list[0]
        res = self.client.get(
                    reverse('horizon:nova:networks:ports:create_ports',
                            kwargs={'network_id': network['id']}))
        self.assertTemplateUsed(res, 'nova/networks/ports/create.html')

    def test_ports_create_post(self):
        network = self.network_list[0]
        port = self.port_list[0]
        self.mox.StubOutWithMock(api, 'quantum_port_create')
        api.quantum_port_create(IsA(http.HttpRequest), 1, network['id'])

        self.mox.ReplayAll()

        formData = {'num': 1,
                    'method': forms.CreatePorts.__name__}
        res = self.client.post(reverse(
                                'horizon:nova:networks:ports:create_ports',
                                kwargs={'network_id': network['id']}),
                              formData)
        self.assertRedirectsNoFollow(res,
                                     reverse(
                                        'horizon:nova:networks:ports:ports',
                                        kwargs={'network_id': network['id']}))

    def test_ports_delete(self):
        network = self.network_list[0]
        port = self.port_list[0]
        self.mox.StubOutWithMock(api, 'quantum_port_delete')
        api.quantum_port_delete(
            IsA(http.HttpRequest),
            network['id'],
            port['id'])

        self.mox.ReplayAll()

        action_string = u"ports__delete__%s" % port['id']
        form_data = {"action": action_string}
        req = self.factory.post(
                    reverse('horizon:nova:networks:ports:ports',
                            kwargs={'network_id': network['id']}), form_data)
        table = PortsTable(req, self.port_list)
        table.kwargs['network_id'] = network['id']
        handled = table.maybe_handle()
        self.assertEqual(handled['location'],
                         reverse('horizon:nova:networks:ports:ports',
                                 kwargs={'network_id': network['id']}))

    def test_ports_attach_post(self):
        network = self.network_list[0]
        port = self.port_list[0]
        self.mox.StubOutWithMock(api, 'quantum_port_attach')
        self.mox.StubOutWithMock(api, 'get_free_interfaces')
        api.quantum_port_attach(IsA(http.HttpRequest),
                                network['id'],
                                port['id'],
                                self.vifs[0]['id'])
        api.get_free_interfaces(IsA(http.HttpRequest)).\
            AndReturn(self.instance_interfaces)

        self.mox.ReplayAll()

        form_data = {'instance': self.vifs[0]['id'],
                     'method': forms.AttachPort.__name__}
        res = self.client.post(reverse(
                                'horizon:nova:networks:ports:attach_port',
                                kwargs={
                                  'network_id': network['id'],
                                  'port_id': port['id']}), form_data)
        self.assertRedirectsNoFollow(res,
                                     reverse(
                                        'horizon:nova:networks:ports:ports',
                                        kwargs={'network_id': network['id']}))

    def test_ports_detach_post(self):
        network = self.network_list[0]
        port = self.port_list[0]
        self.mox.StubOutWithMock(api, 'quantum_port_detach')
        api.quantum_port_detach(IsA(http.HttpRequest),
                                 network['id'],
                                 port['id'])

        self.mox.ReplayAll()

        form_data = {"method": forms.DetachPort.__name__}
        res = self.client.post(
                    reverse('horizon:nova:networks:ports:detach_port',
                            kwargs={
                                'network_id': network['id'],
                                'port_id': port['id']}), form_data)
        self.assertRedirectsNoFollow(res,
                                     reverse(
                                        'horizon:nova:networks:ports:ports',
                                        kwargs={'network_id': network['id']}))

    def test_ports_up(self):
        network = self.network_list[0]
        port = self.port_list[0]
        self.mox.StubOutWithMock(api, 'quantum_ports_toggle')
        api.quantum_ports_toggle(IsA(http.HttpRequest),
                                 network['id'],
                                 port['id'],
                                 'ACTIVE')

        self.mox.ReplayAll()

        action_string = u"ports__turn_port_up__%s" % port['id']
        form_data = {"action": action_string}
        req = self.factory.post(
                    reverse('horizon:nova:networks:ports:ports',
                            kwargs={'network_id': network['id']}), form_data)
        table = PortsTable(req, self.port_list)
        table.kwargs['network_id'] = network['id']
        handled = table.maybe_handle()

    def test_ports_down(self):
        network = self.network_list[0]
        port = self.port_list[0]
        self.mox.StubOutWithMock(api, 'quantum_ports_toggle')
        api.quantum_ports_toggle(IsA(http.HttpRequest),
                                 network['id'],
                                 port['id'],
                                 'DOWN')

        self.mox.ReplayAll()

        action_string = u"ports__turn_port_down__%s" % port['id']
        form_data = {"action": action_string}
        req = self.factory.post(
                    reverse('horizon:nova:networks:ports:ports',
                            kwargs={'network_id': network['id']}), form_data)
        table = PortsTable(req, self.port_list)
        table.kwargs['network_id'] = network['id']
        handled = table.maybe_handle()
        self.assertEqual(handled['location'],
                         reverse('horizon:nova:networks:ports:ports',
                                 kwargs={'network_id': network['id']}))
