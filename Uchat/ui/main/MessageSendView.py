from typing import Optional

from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout


class MessageSendView(QWidget):
    def __init__(self, parent: QWidget, peer_username: Optional[str] = None):
        super().__init__(parent)

        self.layout_manager = QVBoxLayout(self)

        # Text field
        self.__text_field = QPlainTextEdit(self)
        self.__text_field.setPlaceholderText("Message " + (peer_username if peer_username else "chat"))
        self.__text_field.setFixedHeight(100)
        self.layout_manager.addWidget(self.__text_field, 1)

    def text_edit(self) -> QPlainTextEdit:
        """

        :return: The QPlainTextEdit of this widget
        """
        return self.__text_field
