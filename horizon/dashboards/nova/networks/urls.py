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

from django.conf.urls.defaults import *

from .ports import urls as port_urls
from .views import IndexView, CreateNetworkView

NETWORKS = r'^(?P<network_id>[^/]+)/%s$'

# Quantum Networks and Ports
urlpatterns = patterns('horizon.dashboards.nova.networks.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$', CreateNetworkView.as_view(), name='create'),
    url(r'', include(port_urls, namespace='ports'))
)
