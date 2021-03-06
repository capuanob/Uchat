from typing import Optional

from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout, QSizePolicy


class MessageSendView(QWidget):
    """
    Custom widget for multi-line message entry
    """
    def __init__(self, parent: QWidget, peer_username: Optional[str] = None):
        super().__init__(parent)

        self.layout_manager = QVBoxLayout(self)

        # Text field
        self.__text_field = QPlainTextEdit(self)
        self.__text_field.setPlaceholderText("Message " + (peer_username if peer_username else "chat"))
        self.__text_field.setFixedHeight(100)
        self.__text_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout_manager.addWidget(self.__text_field, 1)

    def text_edit(self) -> QPlainTextEdit:
        """
        :return: The QPlainTextEdit of this widget
        """
        return self.__text_field
