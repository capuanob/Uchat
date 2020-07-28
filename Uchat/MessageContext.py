from PyQt5.QtCore import Qt

from Uchat.network.messages.message import Message
from Uchat.peer import Peer


class MessageContext:
    """
    Used for easy transmission of a chat message and contextual information required to process it
    """

    def __init__(self, msg: Message, sender: Peer):
        self.msg = msg
        self.sender = sender
        self.is_sender = sender.is_self()

    def display_flags(self) -> Qt.AlignmentFlag:
        return Qt.AlignRight if self.is_sender else Qt.AlignLeft
