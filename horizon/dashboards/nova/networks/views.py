# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from .forms import CreateNetwork
from .tables import NetworksTable

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = NetworksTable
    template_name = 'nova/networks/index.html'

    def get_data(self):
        try:
            networks = api.quantum_network_list(self.request)
        except:
            networks = []
            msg = _('Unable to retrieve network list.')
            exceptions.handle(self.request, msg)
        return networks


class CreateNetworkView(forms.ModalFormView):
    form_class = CreateNetwork
    template_name = 'nova/networks/create.html'


class GenerateView(View):
    def get(self, request, network_name=None):
        try:
            network = api.quantum_network_create(request, network_name)
        except:
            redirect = reverse('horizon:nova:networks:index')
            exceptions.handle(self.request,
                              _('Unable to create network: %(exc)s'),
                              redirect=redirect)

        response = http.HttpResponse(mimetype='application/binary')
        response['Content-Disposition'] = \
                'attachment; filename=%s.pem' % slugify(keypair.name)
        response.write(keypair.private_key)
        response['Content-Length'] = str(len(response.content))
        return response
