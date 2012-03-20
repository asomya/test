# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from cloudfiles.errors import ContainerNotEmpty
from django import shortcuts
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template.defaultfilters import filesizeformat
from django.utils import http
from django.utils.translation import ugettext as _

from horizon import api
from horizon import tables


LOG = logging.getLogger(__name__)


class DeleteNetworks(tables.DeleteAction):
    data_type_singular = _("Network")
    data_type_plural = _("Networks")

    def delete(self, request, obj_id):
        api.quantum_network_delete(request, obj_id)

    def handle(self, table, request, object_ids):
        # Overriden to show clearer error messages instead of generic message
        deleted = []
        for obj_id in object_ids:
            obj = table.get_object_by_id(obj_id)
            try:
                self.delete(request, obj_id)
                deleted.append(obj)
            except:
                LOG.exception('Unable to delete network "%s".' % obj.name)
                messages.error(request,
                               _('Unable to delete network with ports: %s') %
                               obj.name)
        if deleted:
            messages.success(request,
                             _('Successfully deleted networks: %s')
                               % ", ".join([obj.name for obj in deleted]))
        return shortcuts.redirect('horizon:nova:networks:index')


class CreateNetwork(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Network")
    url = "horizon:nova:networks:create"
    classes = ("ajax-modal", "btn-create")


class NetworksTable(tables.DataTable):
    name = tables.Column("name", link='horizon:nova:networks:ports:ports',
                         verbose_name=_("Network Name"))
    id = tables.Column("id", link='horizon:nova:networks:ports:ports',
                       verbose_name=_("Network id"))
    port_count = tables.Column("port_count", verbose_name=_('Ports'),
                               empty_value="0")

    def get_object_id(self, network):
        return network.id

    class Meta:
        name = "networks"
        verbose_name = _("Networks")
        table_actions = (CreateNetwork, DeleteNetworks,)
        row_actions = (DeleteNetworks,)
