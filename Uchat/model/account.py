from json.encoder import JSONEncoder


class Account:
    """
    Used to store the information associated with the user, specifically the data stored in data/user/global
    """

    def __init__(self, username: str, hex_code: str):
        self.username = username
        self.hex_code = hex_code