"""
All things UPNP
"""
import socket
from enum import Enum

import requests
from miniupnpc import UPnP

from Uchat.helper.globals import LISTENING_PORT, IP_API_URL


class SupportedTransportProtocols(Enum):
    UDP = 0
    TCP = 1


def __is_port_open(external_port: int, protocol: SupportedTransportProtocols) -> bool:
    """
    Used to determine if a local port is open to reach this host from outside the local network
    :param external_port: Port to check
    :param protocol: Protocol of port
    :return: whether or not the port is open
    """

    # Create socket of proper type
    if protocol is SupportedTransportProtocols.TCP:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.settimeout(2)  # Timeout socket after two seconds of no response

    try:
        # Get external API of this host's router (could be behind 1+ NATs)
        https_response = requests.get(IP_API_URL)
        https_response.raise_for_status()
        external_ip = https_response.text

        # Connect to external IP, external port
        sock.connect((external_ip, external_port))
        return True
    except requests.exceptions.HTTPError as err:
        # HTTP Error Occurred

        # Get status code from err

        pass
    except requests.exceptions.RequestException as err:
        # Catch all for requests library
        pass
    except (socket.timeout, OSError) as err:
        # Connection-related exception
        return False


def ensure_port_is_forwarded(external_port: int = LISTENING_PORT, internal_port=LISTENING_PORT):
    """
    Ensures that the given external to internal port mapping has been forwarded to allow inbound connections to this
    host on this port.
    If already done, whether by lack of NAT, firewall, or static port forwarding, no action is taken.
    Otherwise, the port is forwarded dynamically using UPnP (if supported by the router and OS) for the duration of the
    application's runtime.

    :param external_port: Port as viewable from the internet
    :param internal_port: Port as viewable from the LAN
    """

    __is_port_open(external_port, SupportedTransportProtocols.TCP)
    port_forwarded = False
    upnp = UPnP()
    upnp.discoverdelay = 20  # Gives up after 200 ms

    # TODO: Determine if port is already forwarded properly
    # TODO: Determine if UPnP is an enabled service or not
    # TODO: Move all this to a background thread with a callback for UI changes

    # Else
    try:
        discovered_count = upnp.discover()

        if discovered_count > 0:
            upnp.selectigd()
            print(upnp.connectiontype())
            print(upnp.statusinfo())
            port_forwarded = upnp.addportmapping(external_port, 'TCP', upnp.lanaddr, internal_port,
                                                 'UChat P2P Messaging', '')
            __is_port_open(external_port, SupportedTransportProtocols.TCP)
            upnp.deleteportmapping(external_port, 'TCP')

        if not port_forwarded:
            # Send signal to show failure message and how to set up static port forwarding
            pass
    except Exception as e:
        print(type(e))
        print(str(e))
        # TODO: find specific error codes here
        pass
