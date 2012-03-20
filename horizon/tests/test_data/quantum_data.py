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
from horizon.api import quantum
from horizon.api import nova

from novaclient.v1_1 import servers

from .utils import TestDataContainer


def data(TEST):
    TEST.networks = {}
    TEST.network_details = {}
    TEST.ports = {}
    TEST.port_details = {}
    TEST.network_list = []
    TEST.port_list = []
    TEST.instance_interfaces = []

    # Networks
    networks = [{'id': u'5d3ad338-4aea-4f97-a4d8-ad9488da9b49'}]

    networks_dict = {'name': u'private',
                     'id': u'5d3ad338-4aea-4f97-a4d8-ad9488da9b49',
                    }
    network = quantum.Network(networks_dict)
    TEST.networks['networks'] = networks
    TEST.network_details['network'] = networks_dict
    TEST.network_list.append(network)

    # Ports
    ports = [{'id': u'96e9652d-6bdb-4c20-8d79-3eb823540298'}]
    TEST.ports['ports'] = ports

    port_details = {'id': u'96e9652d-6bdb-4c20-8d79-3eb823540298',
                    'state': 'DOWN',
                    'op-state': 'DOWN'
                   }
    TEST.port_details['port'] = port_details

    test_port = {'id':  u'96e9652d-6bdb-4c20-8d79-3eb823540298',
                 'state': 'DOWN',
                 'op-state': 'DOWN',
                 'attachment_id': '1',
                 'attachment_server': 'vm1'
                }
    port = quantum.Port(test_port)
    TEST.port_list.append(port)

    # Attachment
    TEST.port_attachment = {}
    port_attachment = {'id': 'vif1'}
    TEST.port_attachment['attachment'] = port_attachment

    # Instances
    TEST.instances = []
    instance = {'id': '1', 'name': 'instance1'}
    instance_1 = servers.Server(servers.ServerManager(None), instance)
    TEST.instances.append(instance_1)

    # Vifs
    TEST.vifs = []
    vif = {'id': 'vif1'}
    vif_1 = quantum.Vif(vif)

    TEST.vifs.append(vif_1)

    instance_vif = {
                    'instance': 'vm1',
                    'vif': vif_1.id
                   }
    TEST.instance_interfaces.append(instance_vif)
