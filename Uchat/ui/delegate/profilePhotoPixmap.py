from PyQt5.QtCore import QPoint, Qt, QRectF
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush, QFont
from PyQt5.QtWidgets import QApplication


def build_pixmap(color: str, username: str, radius: int = 35) -> QPixmap:
    """
    Generate a pixmap for displaying the profile photo bubble

    :param radius: Radius of circle
    :param color: Hex code to fill the background with
    :param username: Username to draw the first letter from
    :return: a pixmap to be displayed
    """

    pix = QPixmap(radius, radius)
    center_letter = username[0].upper() if username else '?'

    # Convert hex code to RGB values
    color = color.lstrip('#').lstrip('0x')
    hex_len = len(color)
    rgb = tuple(int(color[i:i + hex_len // 3] * (1 if hex_len == 6 else 2), 16) for i in range(0, hex_len, hex_len // 3))

    # Paint background
    pix.fill(QColor("transparent"))

    painter = QPainter(pix)
    painter.setRenderHints(QPainter.Antialiasing, True)
    painter.setBrush(QColor(rgb[0], rgb[1], rgb[2]))
    painter.setPen(Qt.NoPen)

    painter.drawEllipse(0, 0, radius, radius)

    # Paint center_letter
    app_font = QApplication.font()
    app_font.setPixelSize(20)
    painter.setFont(app_font)
    painter.setPen(Qt.white)
    painter.drawText(QRectF(0, 0, radius, radius), Qt.AlignCenter, center_letter)

    return pix
