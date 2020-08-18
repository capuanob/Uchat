"""
All things UPNP
"""
import socket
from enum import Enum

import requests
 # from miniupnpc import UPnP

from Uchat.helper.globals import LISTENING_PORT, IP_API_URL



# def ensure_port_is_forwarded(external_port: int = LISTENING_PORT, internal_port=LISTENING_PORT):
#     """
#     Ensures that the given external to internal port mapping has been forwarded to allow inbound connections to this
#     host on this port.
#     If already done, whether by lack of NAT, firewall, or static port forwarding, no action is taken.
#     Otherwise, the port is forwarded dynamically using UPnP (if supported by the router and OS) for the duration of the
#     application's runtime.
#
#     :param external_port: Port as viewable from the internet
#     :param internal_port: Port as viewable from the LAN
#     """
#
#     __is_port_open(external_port, SupportedTransportProtocols.TCP)
#     port_forwarded = False
#     # upnp = UPnP()
#     # upnp.discoverdelay = 20  # Gives up after 200 ms
#
#     # TODO: Determine if port is already forwarded properly
#     # TODO: Determine if UPnP is an enabled service or not
#     # TODO: Move all this to a background thread with a callback for UI changes
#
#     # Else
#     try:
#         discovered_count = upnp.discover()
#
#         if discovered_count > 0:
#             upnp.selectigd()
#             print(upnp.connectiontype())
#             print(upnp.statusinfo())
#             port_forwarded = upnp.addportmapping(external_port, 'TCP', upnp.lanaddr, internal_port,
#                                                  'UChat P2P Messaging', '')
#             __is_port_open(external_port, SupportedTransportProtocols.TCP)
#             upnp.deleteportmapping(external_port, 'TCP')
#
#         if not port_forwarded:
#             # Send signal to show failure message and how to set up static port forwarding
#             pass
#     except Exception as e:
#         print(type(e))
#         print(str(e))
#         # TODO: find specific error codes here
#         pass
