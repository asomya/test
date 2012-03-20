from django.conf.urls.defaults import patterns, url

from .views import PortsView, CreatePortsView, AttachPortView, DetachPortView

PORTS = r'^(?P<port_id>[^/]+)/%s$'

# Quantum Network Ports
urlpatterns = patterns('horizon.dashboards.nova.networks.ports.views',
    url(
        r'^(?P<network_id>[^/]+)/ports/$',
        PortsView.as_view(),
        name='ports'),
    url(
        r'^(?P<network_id>[^/]+)/create/$',
        CreatePortsView.as_view(),
        name='create_ports'),
    url(
        r'^(?P<network_id>[^/]+)/(?P<port_id>[^/]+)/attach/$',
        AttachPortView.as_view(),
        name='attach_port'),
    url(
        r'^(?P<network_id>[^/]+)/(?P<port_id>[^/]+)/detach/$',
        DetachPortView.as_view(),
        name='detach_port'),
)
