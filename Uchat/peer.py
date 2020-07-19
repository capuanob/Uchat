from typing import Tuple


class Peer:
    """
    Used to represent another client from the user's perspective, stores information necessary for
    communications to them
    """

    def __init__(self, address: Tuple[str, int], is_self: bool):
        self.username = ''
        self.color = ''
        self.is_self = is_self
        self.address = address

    def set_username(self, username: str):
        self.username = username

    def set_color(self, hex_code: str):
        self.color = hex_code

    def set_address(self, address: (str, int)):
        self.address = address
