from typing import Optional
from PyQt5.QtWidgets import QListView, QWidget, QVBoxLayout
from Uchat import MessageContext
from Uchat.conversation import Conversation, debug_conversation
from Uchat.ui.main.MessageSendView import MessageSendView


class ConversationView(QWidget):
    """
    View

    Displays an active conversation, including  all previous messages and a text field for sending new
    messages to the recipient
    """

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        self._layout_manager = QVBoxLayout(self)
        self._message_list = QListView()  # View used to display conversation messages (the model)
        self._conversation_model = debug_conversation()  # Model, contains messages that need to be displayed
        self.send_view = MessageSendView(self, self._conversation_model.peer_username())

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

        self._layout_manager.addWidget(self._message_list)
        self._layout_manager.addWidget(self.send_view)
    # Slots

    def send_message(self, context: MessageContext):
        """
        Used to send a new message in the conversation
        :param context: Context of new chat message to be sent
        """
        pass

    # Signals

    def message_received(self):
        """
        Updates UI to reflect an incoming message that needs to be displayed
        """
        pass


""" TODO
1) Hook up send_view to old send listener (get from ui github)
2) Set up signals and slots for responsive addition
3) Test between two users
4) Stylize
"""