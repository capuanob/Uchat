from PyQt5.QtGui import QPixmap, QColor


def build_pixmap(color: str, username: str) -> QPixmap:
    """
    Generate a pixmap for displaying the profile photo bubble

    :param color: Hex code to fill the background with
    :param username: Username to draw the first letter from
    :return: a pixmap to be displayed
    """

    pix = QPixmap(35, 35)
    center_letter = username[0] if username else '?'

    # Convert hex code to RGB values
    color = color.lstrip('#')
    hex_len = len(color)
    print(color, hex_len)
    rgb = tuple(int(color[i:i + hex_len // 3] * (1 if hex_len == 6 else 2), 16) for i in range(0, hex_len, hex_len // 3))

    # Paint background
    pix.fill(QColor(rgb[0], rgb[1], rgb[2]))
    return pix
