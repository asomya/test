..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================
VLAN trunking networks for NFV
==============================

https://blueprints.launchpad.net/neutron/+spec/nfv-vlan-trunks

Problem description
===================

Many commonly used Neutron plugin configurations create networks that do
not permit VLAN tagged traffic to transit the network.  Some plugins,
conversely, are totally fine at passing all forms of ethernet frame.
It's impossible to tell (via the API) which is in use as a tenant and it's
also impossible to indicate to a plugin what kind of network is required.

VLANs are required for many NFV functions.  This spec proposes making
it possible to request a trunk network - that is, one where VLAN tagged
traffic will be forwarded to other hosts - when one is requested, and
know that a network is in fact a trunk network.

(Other blueprints propose solutions to decomposing trunks into
networks from its individual VLANs, address management on trunk
networks, and so on.  This makes no attempt to address anything other
than the simple L2 properties of networks.  Other blueprints address
higher level concerns such as decomposition of trunks and addressing
of ports with multiple VLANs on, and should use this as a basis to
both get a VLAN transparent network and ensure that the network
they are using is VLAN transparent.)


Proposed change
===============

It is a common requirement of NFV VMs that they talk over many
separate L2 channels.  The number of channels is far in excess of the
number of ports that the VM has and can change over time.  VLAN tags
are often used for separating these channels, so that the number of
ports can be static while still allowing flexibility in the number of
channels.

In Neutron, different network plugins create networks with different
properties, and there is no specific definition of the meaning of the
word 'network'.  Mostly, but not always, networks are L2 broadcast
domains with learning-switch behaviour, although as long as antispoof
filters are in place the network can be implemented either as an L2 or
an L3 domain.  Generally, as long as networks meet a minimum
requirement that IPv4 and IPv6 unicast traffic, ARPs and NDs, work as
expected, no-one will criticise a plugin.

This proposal suggests that a request-discover mechanism be put into
place, so that:

* existing plugins that will pass VLAN tagged traffic can identify
  themselves as such
* existing plugins that cannot pass VLAN tagged traffic can also
  identify themselves as such
* legacy plugins that have not been adapted to report their behaviour
  are identifiable
* future plugins can have selective behaviour, where a network may or
  may not pass VLAN traffic depending on user request - which permits
  the plugin to make decisions in favour of efficiency where the
  functionality is not required (such as using an L3 domain).

Request
-------

During net-create, the user may at their option request that a VLAN
transparent trunk network is created by passing a dict 'requirements'
containing a boolean property 'vlan-transparent' on the net-create
request, set to 'true'.  (Setting the property to 'false' is
equivalent to not specifying the property in the description below.)

Plugins that have not been adapted to understand the 'requirements'
property will ignore this flag and create the network regardless.

Plugins that are aware of the meaning of this property but do not
understand the flag, or cannot deliver VLAN transparent trunk networks,
will refuse to create a network and return an appropriate error to
the user.

Plugins that are aware of this flag and capable of delivering a VLAN
transparent network will do so.

Plugins may change behaviour based on this flag:

- they may create a VLAN transparent network (at higher resource cost)
  if the flag is set, and save on resources when it is not set
- they may refuse to attach certain port types to the network
  (e.g. some external attachment ports may not themselves be VLAN
  transparent and therefore should not be attached to transparent
  networks)

In the case that the flag is absent an aware plugin is under no
obligation to deliver a VLAN transparent network (and an unaware
plugin will, naturally, ignore its absence); the returned network may
or may not be VLAN transparent.

Response
--------

After network creation, a network may have a property
'requirements' containing a flag property 'vlan-transparent'.

In the case that this property does not exist, the plugin
is a legacy plugin and no determination is possible about whether the
network is capable of passing VLAN tagged packets.

In the case that the property exists and the flag is set to true, then
the plugin is a VLAN aware plugin and (regardless of the request)
has created a network capable of passing VLAN tagged packets.

In the case that the property exists and the flag is set to false,
then the plugin is a VLAN aware plugin, the request did not pass the
'vlan-transparent' flag, and for its own reasons the plugin
elected to create a network without VLAN transparency (typically
because it's being efficient or it's simply not capable of doing so).

Per the description in 'request' above, it is possible that the correct
response is an error indicating inability to act upon the request.

Firewalling
-----------

VLAN tagging will be treated as an opaque encapsulation.

VLAN tagged packets will *not* be firewalled by security groups or other
port based security such as antispoofing, as the packet is not an IP
packet.  (For those drivers capable of passing VLAN tagged packets, this
is - at least sometimes - a change of behaviour.)

This is in keeping with the behaviour for other non-IP
packet types such as MPLS (itself an encap type). 


Alternatives
------------

None

Data model impact
-----------------

'requirements' property added to networks containing an
arbitrary set of properties (for future expansion).  'vlan-transparent'
would be the only understood property.  'requirements' should be
an empty dict when upgrading old datamodels, indicating indeterminate
status.

REST API impact
---------------

requirements property, vlan-transparent attribute: new arguments to
net-create, optional (thus backward compatible); new results to
net-show, similarly optional if not supported and therefore
backward compatible.

Security impact
---------------

In current implementations that do pass VLANs, tagged packets'
contents are firewalled.  This is not explicitly documented, but is
one behaviour a user might reasonably expect.

This change proposes treating a VLAN tag as an opaque encapsulation,
and thus VLAN tagged packets would *not* be firewalled by their
content.  Also, security groups only offer IP-based firewalling, so
it would not be possible to block VLAN tagged packets.  That said,
guest OSes can be expected to ignore tagged packets when not
configured for receipt of VLANs, so there should be no impact.

This is in keeping with the behaviour for other non-IP
packet types such as MPLS (itself an encap type). 

Notifications impact
--------------------

None

Other end user impact
---------------------

The python-neutronclient should be adjusted to take account of the new
option for net-create and the new property in net-show.

Performance Impact
------------------

May make some plugins more efficient at using network resources.

Other deployer impact
---------------------

None.

Developer impact
----------------

None.

Implementation
==============

Assignee(s)
-----------

ijw-ubuntu

Work Items
----------

* Implement new net-create parameter
* Implement new network property, including database migration script
* Change a sampling of plugins, including the ML2 plugin, to implement
  use of the properties

Dependencies
============

None

Testing
=======

Tempest should confirm that (for a known good networking setup) VLAN
transparent networks can be requested and that they work.  Such testing
should ideally be host to host, to test both the soft switch and the
hardware configuration.

Documentation Impact
====================

Requires documentation of the new flag, and more general documentation
of the use and meaning of the 'requirements' property so that it is
available for future use.

References
==========

 - https://etherpad.openstack.org/p/juno-nfv-bof
 - https://review.openstack.org/#/c/92541/ (composite port support, which
   is independent of the status of an individual network)
 - https://review.openstack.org/#/c/87825/ (external attachments, which
   may use VLANs but again doesn't mandate that a Neutron network
   passes tagged traffic as it's more involved with the under-the-API
   networking)
