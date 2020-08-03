from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QListView, QWidget, QVBoxLayout, QPlainTextEdit

from Uchat.client import Client
from Uchat.network.messages.message import ChatMessage
from Uchat.ui.main.MessageSendView import MessageSendView


class ConversationView(QWidget):
    """
    View

    Displays an active conversation, including  all previous messages and a text field for sending new
    messages to the recipient
    """

    def __init__(self, parent: Optional[QWidget], conv_idx: int, client: Client):
        super().__init__(parent)

        self._layout_manager = QVBoxLayout(self)
        self._message_list = QListView()  # View used to display conversation messages (the model)
        self._conversation_model = client.conversation(conv_idx)  # Model, contains messages that need to be displayed
        self._idx = conv_idx  # Index of conversation, for use with client interaction
        self._client = client
        self._send_view = MessageSendView(self,
                                          self._conversation_model.peer().username() if self._conversation_model else None)

        self.setup_ui()

    def setup_ui(self):
        """
        Builds UI for display
        """

        self._message_list.setModel(self._conversation_model)  # Connect model
        self._message_list.setLayoutMode(QListView.Batched)  # Display as needed
        self._message_list.setBatchSize(10)  # Number of messages to display
        self._message_list.setFlow(QListView.TopToBottom)  # Display vertically
        self._message_list.setResizeMode(QListView.Adjust)  # Items laid out every time view is resized

        # Set custom size hint, based off viewport size hint
        # vp_size_hint_func = (lambda: QSize(self._message_list.sizeHintForColumn(0),
        # self._message_list.sizeHintForRow(0) * self._conversation_model.rowCount()))
        # self._message_list.sizeHint = vp_size_hint_func

        # Connect to signals
        self._send_view.text_edit().keyPressEvent = self.send_view_did_change
        self._message_list.verticalScrollBar().rangeChanged.connect(self.scroll_to_message)

        # Layout widgets and views
        self._layout_manager.addStretch(1)
        self._layout_manager.addWidget(self._message_list)
        self._layout_manager.addWidget(self._send_view)

    # Listeners

    def send_view_did_change(self, event: QKeyEvent):
        """
        As QPlainTextEdit doesn't natively support enter key response, this function prevents the user from typing the
        'enter' key and sends a message on its press instead
        :param event: QKeyEvent raised by key press
        """

        text_field = self._send_view.text_edit()

        if event.key() == Qt.Key_Return:
            message: str = text_field.toPlainText()

            if not message:  # Don't want to allow sending of empty messages
                return

            # Clear message send view
            self._send_view.text_edit().clear()

            # Create message
            chat_msg = ChatMessage(message)

            # Send over network to peer
            self._client.send_chat(self._idx, chat_msg)
        else:
            QPlainTextEdit.keyPressEvent(text_field, event)

    def scroll_to_message(self):
        """
        Event Listener connected to QListView's vertical scroll bar's range change

        Scrolls to a new message when view reflects a new message in the model
        """

        self._message_list.scrollToBottom()
