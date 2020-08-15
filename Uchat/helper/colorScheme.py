"""
Helper functions that deal with the application's color scheme
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush, QImage, QPen


def load_themed_icon(file_path: str, color: QColor) -> QIcon:
    """
    Loads an icon, paints it the given color, and builds an icon
    :param file_path: Path where the icon is stored, to be loaded as a pixmap
    :param color: Color to paint pixmap
    :return: a new QIcon containing the photo at file_path
    """

    photo_pixmap = QPixmap(file_path)
    themed_pixmap = QPixmap(photo_pixmap.size())

    themed_pixmap.fill(color)
    themed_pixmap.setMask(photo_pixmap.createMaskFromColor(Qt.transparent))

    return QIcon(themed_pixmap)
