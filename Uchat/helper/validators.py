"""
Functions that can be used throughout the program for validating user input
"""


def is_valid_ipv4(txt: str):
    """
    Determines whether the given input is a valid IPv4 address (0-255.0-255.0-255.0-255)
    :param txt: A possible IPv4
    :return: whether or not the txt is a valid IPv4
    """
    ip_bytes = txt.split('.')

    return len(ip_bytes) == 4 and all(0 <= (int(byte) if byte.isdigit() else -1) <= 255 for byte in ip_bytes)


def is_valid_port(txt: str):
    """
    Determines whether the given input is a valid port number (0-65535)
    :param txt: A possible port number
    :return: whether or not the txt is a valid port number
    """

    return txt.isdigit() and 0 <= int(txt) <= 65535
