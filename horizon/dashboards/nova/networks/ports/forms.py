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

import logging

from django import shortcuts
from django.contrib import messages
from django.core import validators
from django.utils.translation import ugettext as _
from novaclient import exceptions as novaclient_exceptions

from horizon import api
from horizon import exceptions
from horizon import forms

import re
import pprint

LOG = logging.getLogger(__name__)


class CreatePorts(forms.SelfHandlingForm):
    num = forms.IntegerField(max_value="256",
                              label=_("Number of ports"),
                              validators=[validators.validate_slug],
                              error_messages={'invalid': _('Port numbers may '
                                              'only contain numbers')})

    def handle(self, request, data):
        uri = request.get_full_path()
        match = re.search('/nova/networks/([^/]+)/create', uri)
        network_id = match.group(1)
        try:
            api.quantum_port_create(request, data['num'], network_id)
            messages.success(request, _("Ports created successfully."))
        except:
            exceptions.handle(request, _('Unable to create Ports.'))
        return shortcuts.redirect(
            "horizon:nova:networks:ports:ports",
            network_id=network_id)


class AttachPort(forms.SelfHandlingForm):
    instance = forms.ChoiceField(label=("Select instance"),
                                 widget=forms.Select(
                                 attrs={'class': 'switchable'}))

    def __init__(self, *args, **kwargs):
        super(AttachPort, self).__init__(*args, **kwargs)
        initials = kwargs.get("initial", {})
        interfaces = initials.get('interfaces', [])
        interface_choices = []

        for interface in interfaces:
            interface_choices.append((interface['vif'], interface['instance']))

        self.fields['instance'].choices = interface_choices

    def handle(self, request, data):
        uri = request.get_full_path()
        match = re.search('/nova/networks/([^/]+)/([^/]+)/attach', uri)
        network_id = match.group(1)
        port_id = match.group(2)

        try:
            api.quantum_port_attach(request,
                                    network_id,
                                    port_id,
                                    data['instance'])
            messages.success(request, _("Port attached successfully."))
        except:
            exceptions.handle(request, _('Unable to attach Port.'))
        return shortcuts.redirect(
            "horizon:nova:networks:ports:ports",
            network_id=network_id)


class DetachPort(forms.SelfHandlingForm):

    def handle(self, request, data):
        uri = request.get_full_path()
        match = re.search('/nova/networks/([^/]+)/([^/]+)/detach', uri)
        network_id = match.group(1)
        port_id = match.group(2)

        try:
            api.quantum_port_detach(request, network_id, port_id)
            messages.success(request, _("Port detached successfully."))
        except:
            exceptions.handle(request, _('Unable to detach Port.'))
        return shortcuts.redirect(
            "horizon:nova:networks:ports:ports",
            network_id=network_id)
