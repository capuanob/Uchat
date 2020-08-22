"""
All things UPNP
"""
from enum import Enum

from miniupnpc import UPnP

from Uchat.helper.error import print_err
from Uchat.helper.globals import LISTENING_PORT


class SupportedTransportProtocols(Enum):
    UDP = 'UDP'
    TCP = 'TCP'


# THREADED
def ensure_port_is_forwarded(protocol: SupportedTransportProtocols = SupportedTransportProtocols.TCP,
                             external_port: int = LISTENING_PORT, internal_port=LISTENING_PORT):
    """
    Ensures that the given external to internal port mapping has been forwarded to allow inbound connections to this
    host on this port.
    If already done, whether by lack of NAT, firewall, or static port forwarding, no action is taken.
    Otherwise, the port is forwarded dynamically using UPnP (if supported by the router and OS) for the duration of the
    application's runtime.

    :param protocol: Transport protocol of port to be mapped
    :param external_port: Port as viewable from the internet
    :param internal_port: Port as viewable from the LAN
    """
    upnp = UPnP()
    upnp.discoverdelay = 20  # Gives up after 20 ms

    port_forwarded = False
    discovered_count = upnp.discover()

    if discovered_count > 0:
        upnp.selectigd()
        port_forwarded = upnp.addportmapping(external_port, protocol.value, upnp.lanaddr, internal_port,
                                             'UChat P2P Messaging', '')

    if not port_forwarded:
        # Send signal to show failure message and how to set up static port forwarding
        print_err(2, "Unable to open UPnP {} port {}".format(protocol.value, external_port))
    print("UPnP Port Mapping added")


def delete_port_mapping(protocol: SupportedTransportProtocols = SupportedTransportProtocols.TCP,
                        external_port: int = LISTENING_PORT):
    """
    Removes any UPnP temporary port forwards, to be executed on the application's closure
    :param protocol: Transport protocol of port to be deleted
    :param external_port: Port as viewable from internet
    """

    port_forward_deleted = False
    upnp = UPnP()
    upnp.discoverdelay = 20  # Gives up after 20 ms

    try:
        discovered_count = upnp.discover()
        if discovered_count > 0:
            upnp.selectigd()
            port_forward_deleted = upnp.deleteportmapping(external_port, protocol.value)
        if not port_forward_deleted:
            # Send signal to show failure message and how to set up static port forwarding
            print_err(2, "Failed to delete UPnP Port Mapping on {} port {}".format(protocol.value, external_port))
            pass
    except Exception as e:
        print(type(e))
        print(str(e))
        pass
    print("UPnP Port Mapping Deleted")
