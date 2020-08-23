"""
Functions for helping with IP
"""
import socket
from enum import Enum
from typing import Optional

import requests

from Uchat.helper.globals import IP_API_URL, IP_API_FAILSAFE_URL


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
        external_ip = get_http_response(IP_API_URL)

        # Connect to external IP, external port
        sock.connect((external_ip, external_port))
        return True
    except requests.exceptions.HTTPError as err:
        # HTTP Error Occurred

        # Get status code from err

        pass
    except requests.exceptions.RequestException as err:
        # Catch all for requests library
        external_ip = get_http_response(IP_API_FAILSAFE_URL)
        pass
    except (socket.timeout, OSError) as err:
        # Connection-related exception
        return False


def get_http_response(url: str, return_json: bool) -> Optional[str]:
    """
    Function gets HTTP response from given URL
    :param url: url for rest API
    :param return_json: bool to check if HTTP response is JSON object or anything else
    :return: string holding the IP address
    """
    try:
        https_response = requests.get(url)
        https_response.raise_for_status()
        if return_json:
            # If the return type from the API is a JSON object, extract IP
            json_obj = https_response.json()
            external_ip = json_obj.get('ip', None)
        else:
            external_ip = https_response.text
        return external_ip
    except requests.exceptions.RequestException as err:
        return None


def get_external_ip() -> Optional[str]:
    """
    :return: Either string holding IP address, or None to show no IP was able to be found
    """
    if not (external_ip := get_http_response(IP_API_URL, False)):
        external_ip = get_http_response(IP_API_FAILSAFE_URL, True)
    return external_ip


