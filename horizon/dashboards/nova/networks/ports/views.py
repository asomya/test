# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright Cisco Systems Inc.
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

"""
Views for managing Nova keypairs.
"""
import logging

from django import http
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.views.generic import View, TemplateView
from django.utils.translation import ugettext as _

from horizon import api
from horizon import forms
from horizon import tables
from horizon import exceptions

from .forms import CreatePorts, AttachPort, DetachPort
from .tables import PortsTable

import pickle
LOG = logging.getLogger(__name__)


class CreatePortsView(forms.ModalFormView):
    form_class = CreatePorts
    template_name = 'nova/networks/ports/create.html'


class PortsView(tables.DataTableView):
    table_class = PortsTable
    template_name = 'nova/networks/ports/index.html'

    def get_data(self):
        network_id = self.kwargs['network_id']
        try:
            ports = api.quantum_port_list(self.request, network_id)
        except:
            ports = []
            msg = _('Unable to retrieve network details.')
            exceptions.handle(self.request, msg)
        return ports


class AttachPortView(forms.ModalFormView):
    form_class = AttachPort
    template_name = 'nova/networks/ports/attach.html'

    def get_initial(self):
        interfaces = api.get_free_interfaces(self.request)
        return {"interfaces": interfaces}


class DetachPortView(forms.ModalFormView):
    form_class = DetachPort
    template_name = 'nova/networks/ports/detach.html'
