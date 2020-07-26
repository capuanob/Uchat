from typing import Tuple, Optional


class Peer:
    """
    Used to represent another client from the user's perspective, stores information necessary for
    communications to them
    """

    def __init__(self, address: Tuple[str, int], is_self: bool, username: Optional[str] = '', color: Optional[str] = ''):
        self.__username = username
        self.__color = color
        self.__is_self = is_self
        self.__address = address

    def username(self, new_username: Optional[str] = None):
        if new_username:
            self.__username = new_username
        return self.__username

    def color(self, new_color: Optional[str] = None):
        if new_color:
            self.__color = new_color
        return self.__color

    def color_as_int(self):
        """
        Converts the hexadecimal color code to its integer representation
        :return:
        """

        hex_color = self.__color if self.__color[0] != '#' else self.__color[1:]  # Drop the hash
        return int(hex_color, 16)

    def address(self, new_address: Optional[Tuple[str, int]] = None):
        if new_address:
            self.__address = new_address
        return self.__address

    def is_self(self):
        return self.__is_self
