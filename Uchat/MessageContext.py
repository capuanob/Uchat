from PyQt5.QtCore import Qt

from Uchat.network.messages.message import ChatMessage
from Uchat.peer import Peer


class MessageContext:
    """
    Used for easy transmission of a chat message and contextual information required to process it
    """

    def __init__(self, chat_msg: ChatMessage, sender: Peer):
        self.msg = chat_msg
        self.sender = sender
        self.is_sender = sender.is_self

    def display_flags(self) -> Qt.AlignmentFlag:
        return Qt.AlignRight if self.is_sender else Qt.AlignLeft


_DEBUG_SELF = Peer(('192.167.03.1', 4050), True)
_DEBUG_SELF.set_username('nokillz')
_DEBUG_SELF.set_color('#FAB')
_DEBUG_PEER = Peer(('128.0.0.1', 4030), False)
_DEBUG_PEER.set_username('PhilWasTaken')
_DEBUG_PEER.set_color('#9AB20A')

DEBUG_MESSAGES = [
    MessageContext(ChatMessage('What is up?'), _DEBUG_SELF),
    MessageContext(ChatMessage('Not too much, hbu?'), _DEBUG_PEER),
    MessageContext(ChatMessage("I've just been studying chimpanzees today."), _DEBUG_PEER),
    MessageContext(ChatMessage("You must listen to the Joe Rogan Experience, a syndicated podcast available on the\
 Apple app store! It's really a good podcast."), _DEBUG_SELF),
    MessageContext(ChatMessage("Yeah, well anyways you see that Phil had his nuts out in a pic?"), _DEBUG_PEER),
    MessageContext(ChatMessage("Funniest shit I ever seen."), _DEBUG_SELF),
    MessageContext(ChatMessage("O-oooooooooo AAAAE-A-A-I-A-U- JO-oooooooooooo AAE-O-A-A-U-U-A- E-eee-ee-eee\
AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA"), _DEBUG_PEER),
]
