"""
Defines the custom delegate used for displaying messages in a QListView
"""
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QObject, Qt, QSize, QRect
from PyQt5.QtGui import QFontMetrics, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QApplication


class MessageItemDelegate(QStyledItemDelegate):
    """
    Item delegate used for displaying a message according to the desired style
    """

    icon_radius = 35
    profile_padding = 20
    padding = 20
    total_pfp_width = icon_radius + profile_padding

    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
        if not index.isValid():
            return QSize()

        context = index.model().chat_message_contexts()[index.row()]

        msg_text = index.data(Qt.DisplayRole)
        msg_font = QApplication.font()
        msg_fm = QFontMetrics(msg_font)

        msg_rect = msg_fm.boundingRect(0, 0,
                                       option.rect.width() - MessageItemDelegate.total_pfp_width
                                       + MessageItemDelegate.profile_padding, 0,
                                       Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, msg_text)

        msg_size = QSize(option.rect.width(),
                         msg_rect.height() + MessageItemDelegate.padding + MessageItemDelegate.profile_padding)

        if msg_size.height() < MessageItemDelegate.icon_radius:
            msg_size.setHeight(MessageItemDelegate.icon_radius)

        return msg_size

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        """
        Paints the message on the screen

        :param painter: Controls actual painting
        :param option: Options for painting
        :param index: Index of item
        :return:
        """

        if not index.isValid():
            return

        painter.save()  # Save current state, before altering for custom painting

        painter.setRenderHints(QPainter.Antialiasing)

        context = index.model().chat_message_contexts()[index.row()]
        message_text = index.data(Qt.DisplayRole)
        profile_pix: QPixmap = index.data(Qt.DecorationRole)

        # Determine message rect
        message_font = QApplication.font()
        message_fm = QFontMetrics(message_font)

        if context.is_sender:
            # Paint text with 10 pixel padding
            message_rect = message_fm.boundingRect(option.rect.left(),
                                                   option.rect.top() + MessageItemDelegate.profile_padding / 2,
                                                   option.rect.width() - MessageItemDelegate.total_pfp_width,
                                                   0,
                                                   Qt.AlignRight | Qt.AlignTop | Qt.TextWordWrap, message_text)

            # Draw bubble rect
            bubble_rect = QRect(message_rect.left() - MessageItemDelegate.profile_padding / 2,
                                message_rect.top() - MessageItemDelegate.profile_padding / 2,
                                message_rect.width() + MessageItemDelegate.profile_padding,
                                message_rect.height() + MessageItemDelegate.profile_padding)
            blue = QColor(35, 57, 93)
            painter.setBrush(blue)
            painter.setPen(blue)
            painter.drawRoundedRect(bubble_rect, 5, 5)

            painter.setPen(Qt.white)
            painter.setFont(message_font)
            painter.drawText(message_rect, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, message_text)

            # Paint icon
            profile_rect = QRect(message_rect.right() + MessageItemDelegate.profile_padding, option.rect.top(),
                                 MessageItemDelegate.icon_radius, MessageItemDelegate.icon_radius)
            painter.drawPixmap(profile_rect, profile_pix)
        else:

            # Paint icon
            profile_rect = QRect(option.rect.left(), option.rect.top(),
                                 MessageItemDelegate.icon_radius, MessageItemDelegate.icon_radius)
            painter.drawPixmap(profile_rect, profile_pix)

            # Paint text with 10 pixel padding
            message_rect = message_fm.boundingRect(profile_rect.right() + MessageItemDelegate.profile_padding,
                                                   option.rect.top() + MessageItemDelegate.profile_padding / 2,
                                                   option.rect.width() - MessageItemDelegate.total_pfp_width, 0,

                                                   Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, message_text)

            # Draw bubble rect
            bubble_rect = QRect(message_rect.left() - MessageItemDelegate.profile_padding / 2,
                                message_rect.top() - MessageItemDelegate.profile_padding / 2,
                                message_rect.width() + MessageItemDelegate.profile_padding,
                                message_rect.height() + MessageItemDelegate.profile_padding)
            gray = QColor(105, 105, 105)
            painter.setBrush(gray)
            painter.setPen(gray)
            painter.drawRoundedRect(bubble_rect, 5, 5)

            painter.setPen(Qt.white)
            painter.setFont(message_font)
            painter.drawText(message_rect, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, message_text)

        painter.restore()  # Reset to state before changes
        # super().paint(painter, option, index)
