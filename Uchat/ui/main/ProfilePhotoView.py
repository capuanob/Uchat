from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel


def validate_hex_code(hex_code: str) -> str:
    """
    Ensures a given hex code is in a uniform format #HHHHHH or #HHH
    :param hex_code: Possibly incompatible hex string, definitely contains proper characters though
    :return: a valid hex_code
    """
    hex_len = len(hex_code)

    if hex_code and hex_code[0] == '#':
        if hex_len in (4, 7):
            return hex_code
        return ''
    elif hex_len in (3, 6):
        return '#' + hex_code
    else:
        return ''


class ProfilePhotoView(QLabel):
    """
    This class is used to display a user's profile photo
    Given their username and a hex color code, a proper profile photo is generated
    """

    def __init__(self, parent: QWidget, username: str = '', hex_code: str = '', radius: int = 35):
        super().__init__(parent)
        self.setObjectName('pfp-view')

        diameter = radius * 2
        self.setStyleSheet(
            """
            color: white;
            font-size: {}px;
            border-radius: {}px;
            """.format(radius + 10, radius))
        self.setMinimumSize(diameter, diameter)
        self.setAlignment(Qt.AlignCenter)
        self.update_label(username, hex_code)

    def update_label(self, username: str, hex_code: str):
        """
        Updates profile photo's color and displayed username
        :param username: Username to extract first letter from
        :param hex_code: Hex code string to use as profile background
        """

        __hex_code = validate_hex_code(hex_code)
        self.setStyleSheet(self.styleSheet() +
                           """
            background-color: {};
            """.format(__hex_code if hex_code else '#6d0d7a'))
        self.setText(username[0].upper() if username else 'U')
