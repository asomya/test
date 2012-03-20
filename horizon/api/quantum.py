# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Cisco Systems Inc.
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

from __future__ import absolute_import

import functools
import logging
import urlparse

from django.utils.decorators import available_attrs

import quantumclient as quantum_client
from quantumclient.common import exceptions as quantum_exception

from horizon.api.base import APIDictWrapper, url_for
from horizon.api import nova

LOG = logging.getLogger(__name__)


class Network(APIDictWrapper):
    _attrs = ['id', 'name', 'port_count']


class Port(APIDictWrapper):
    _attrs = ['id', 'attachment_server', 'attachment_id', 'state', 'op-status']


class Vif(APIDictWrapper):
    _attrs = ['id']


def quantumclient(request):
    o = urlparse.urlparse(url_for(request, 'network'))
    LOG.debug('quantum client connection created for host "%s:%d"' %
              (o.hostname, o.port))
    return quantum_client.Client(o.hostname,
                                 o.port,
                                 tenant=request.user.tenant_id,
                                 auth_token=request.user.token)


def quantum_network_list(request):
    q_networks = quantumclient(request).list_networks()
    networks = []
    for network in q_networks['networks']:
        # Get detail for this network
        det = quantumclient(request).show_network_details(network['id'])
        # Get ports for this network
        ports = quantumclient(request).list_ports(network['id'])
        det['network']['port_count'] = len(ports['ports'])
        networks.append(Network(det['network']))
    return networks


def quantum_network_create(request, n_name):
    data = {'network': {'name': n_name}}
    return quantumclient(request).create_network(data)


def quantum_network_delete(request, n_uuid):
    return quantumclient(request).delete_network(n_uuid)


def quantum_network_update(request, *args):
    tenant_id, network_id, param_data, version = args
    data = {'network': {}}
    for kv in param_data.split(","):
        k, v = kv.split("=")
        data['network'][k] = v
    data['network']['id'] = network_id

    return quantumclient(request).update_network(network_id, data)


def quantum_network_details(request, n_uuid):
    details = quantumclient(request).show_network_details(n_uuid)
    return details


def quantum_port_list(request, n_uuid):
    q_ports = quantumclient(request).list_ports(n_uuid)
    ports = []
    for port in q_ports['ports']:
        # Get port details
        det = quantumclient(request).show_port_details(n_uuid, port['id'])
        att = quantumclient(request).show_port_attachment(n_uuid, port['id'])
        # Get server name from id
        if 'id' in att['attachment']:
            server = get_interface_server(request, att['attachment']['id'])
            det['port']['attachment_server'] = server.name
            det['port']['attachment_id'] = att['attachment']['id']
        else:
            det['port']['attachment_id'] = None
            det['port']['attachment_server'] = None
        ports.append(Port(det['port']))
    return ports


def quantum_port_create(request, num, uuid):
    for i in range(int(num)):
        quantumclient(request).create_port(uuid)


def quantum_port_delete(request, n_uuid, p_uuid):
    return quantumclient(request).delete_port(n_uuid, p_uuid)


def quantum_port_update(request, *args):
    tenant_id, network_id, port_id, param_data, version = args
    data = {'port': {}}
    for kv in param_data.split(","):
        k, v = kv.split("=")
        data['port'][k] = v
    data['network_id'] = network_id
    data['port']['id'] = port_id

    return quantumclient(request).update_port(network_id, port_id, data)


def quantum_port_attach(request, network_id, port_id, attachment):
    data = {'attachment': {'id': '%s' % attachment}}

    return quantumclient(request).attach_resource(network_id, port_id, data)


def quantum_port_detach(request, network_id, port_id):
    return quantumclient(request).detach_resource(network_id, port_id)


def quantum_ports_toggle(request, network_id, port_id, state):
    data = {'port': {'state': state}}
    return quantumclient(request).update_port(network_id, port_id, data)


def get_free_interfaces(request):
    instance_interfaces = []
    attached_interfaces = []
    # Fetch a list of networks
    networks = quantum_network_list(request)
    for network in networks:
        # Get all ports
        ports = quantum_port_list(request, network.id)
        for port in ports:
            # Check for attachments
            if port.attachment_id:
                attached_interfaces.append(port.attachment_id)

    # Get all instances
    instances = nova.server_list(request)
    for instance in instances:
        vifs = nova.virtual_interfaces_list(request, instance.id)
        for vif in vifs:
            if not any(vif.id in s for s in attached_interfaces):
                instance_interfaces.append(
                {'instance': instance.name, 'vif': vif.id})
    return instance_interfaces


def get_interface_server(request, interface):
    # Get all instances
    instances = nova.server_list(request)
    for instance in instances:
        vifs = nova.virtual_interfaces_list(request, instance.id)
        for vif in vifs:
            if vif.id == interface:
                return instance
    return None
