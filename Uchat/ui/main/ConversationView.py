from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit

from Uchat.MessageContext import DEBUG_MESSAGES, MessageContext, _DEBUG_SELF
from Uchat.network.messages.message import ChatMessage
from Uchat.ui.main.ChatAreaView import ChatAreaView
from Uchat.ui.main.MessageSendView import MessageSendView


class ConversationView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.__layout_manager = QVBoxLayout(self)

        self.__chat_area = ChatAreaView(self, DEBUG_MESSAGES)
        self.__send_view = MessageSendView(self)

        # Layout widgets
        self.__layout_manager.addStretch(1)
        self.__layout_manager.addWidget(self.__chat_area.central_widget())
        self.__layout_manager.addWidget(self.__send_view)

        # Set up event listeners and responders
        self.__send_view.text_edit().keyPressEvent = self.key_pressed

    def key_pressed(self, e: QKeyEvent):
        """
        As QPlainTextEdit doesn't natively support enter key response, this function prevents the user from typing the
        'enter' key and sends a message on its press instead
        :param e: QKeyEvent raised by key press
        :return: void
        """
        text_field = self.__send_view.text_edit()

        if e.key() == Qt.Key_Return:
            message = text_field.toPlainText()

            if not message:  # Don't want to allow sending of empty messages
                return

            # Clear message send view
            self.__send_view.text_edit().clear()

            # Send message over network
            chat_msg = ChatMessage(message)
            chat_context = MessageContext(chat_msg, _DEBUG_SELF)

            # Update UI with new message
            self.__chat_area.update_with(chat_context)
        else:
            QPlainTextEdit.keyPressEvent(text_field, e)
