from typing import Optional


class Account:
    """
    Used to store the information associated with the user, specifically the data stored in data/user/global
    """

    def __init__(self, username: str = '', hex_code: str = '', allows_UPnP: bool = False):
        self.__username = username
        self.__hex_code = hex_code
        self.__allows_UPnP = allows_UPnP

    def username(self, new_username: Optional[str] = None) -> str:
        if new_username:
            self.__username = new_username
        return self.__username

    def hex_code(self, new_hex: Optional[str] = None) -> str:
        if new_hex:
            self.__hex_code = new_hex
        return self.__hex_code

    def upnp(self, new_status: Optional[bool] = None) -> bool:
        if new_status is not None:
            self.__allows_UPnP = new_status
        return self.__allows_UPnP
