from typing import Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QListView, QWidget, QVBoxLayout, QPlainTextEdit, QFrame, QLabel, QSizePolicy, QHBoxLayout

from Uchat.client import Client
from Uchat.model.peerList import PeerList
from Uchat.network.messages.message import ChatMessage
from Uchat.peer import Peer
from Uchat.ui.delegate.messageItemDelegate import MessageItemDelegate
from Uchat.ui.main.MessageSendView import MessageSendView
from Uchat.ui.main.ProfilePhotoView import ProfilePhotoView


class ConversationView(QFrame):
    """
    View

    Displays an active conversation, including  all previous messages and a text field for sending new
    messages to the recipient
    """

    def __init__(self, parent: Optional[QWidget], client: Client, peer: Peer,
                 friends_list: PeerList, conversation_list: PeerList):

        super().__init__(parent)
        self.setObjectName("conversation_view")

        self._peer = peer
        self._client = client
        self._friends_list = friends_list
        self._conversation_list = conversation_list
        self._conversation_model = self._client.conversation(self._peer)  # Model containing messages
        self._layout_manager = QVBoxLayout(self)

        # Configure message list
        self._message_list = QListView()  # View used to display conversation messages (the model)
        self._message_list.setWordWrap(True)
        self._message_list.setModel(self._conversation_model)

        # Set up custom delegate
        message_delegate = MessageItemDelegate(self._message_list)
        self._message_list.setItemDelegate(message_delegate)
        self._send_view = MessageSendView(self,
                                          self._conversation_model.peer().username() if self._conversation_model else None)
        self.setup_ui()

    def setup_ui(self):
        """
        Builds UI for display
        """

        self._layout_manager.setContentsMargins(0, 0, 0, 0)
        self._send_view.setContentsMargins(0, 0, 0, 0)

        self._message_list.setModel(self._conversation_model)  # Connect model
        self._message_list.setLayoutMode(QListView.Batched)  # Display as needed
        self._message_list.setBatchSize(10)  # Number of messages to display
        self._message_list.setFlow(QListView.TopToBottom)  # Display vertically
        self._message_list.setResizeMode(QListView.Adjust)  # Items laid out every time view is resized

        # TODO: Build header


        # Layout widgets and views
        # self._layout_manager.addWidget(header)
        self._layout_manager.addWidget(self._message_list, 1)
        self._layout_manager.addWidget(self._send_view)

        # Connect to signals
        self._send_view.text_edit().keyPressEvent = self.send_view_did_change
        self._message_list.verticalScrollBar().rangeChanged.connect(self.scroll_to_message)

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
            self._client.send_chat(self._peer, chat_msg)
        else:
            QPlainTextEdit.keyPressEvent(text_field, event)

    def scroll_to_message(self):
        """
        Event Listener connected to QListView's vertical scroll bar's range change

        Scrolls to a new message when view reflects a new message in the model
        """

        self._message_list.scrollToBottom()
