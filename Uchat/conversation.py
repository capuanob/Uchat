from enum import Enum
from typing import List, Set

from Uchat.network.messages.message import Message, FarewellMessage, GreetingMessage, \
    MessageType
from Uchat.peer import Peer


class ConversationState(Enum):
    """
    If viewing a conversation as a Finite State Automota, this would be it's current state
    See docs for the respective FSM for reference
    """
    INACTIVE = 0  # Newly created conversation, no action has been taken by any participant
    AWAIT = 1  # A user has sent it's peer a greeting that has not yet been responded to
    ACTIVE = 2  # The requesting client ('requester') has received a conversation acceptance request, can now chat
    CLOSED = 3  # The conversation is permanently closed, whether to declination or a participant leaving after chatting


class Conversation:
    """
    A conversation is held between two or more clients. A client can be engaged in multiple, simultaneous conversations.
    Responsible for tracking messages sent during current conversation, it's participants, and it's status
    """

    def __init__(self, peer_addr: (str, int)):
        self._state: ConversationState = ConversationState.INACTIVE
        self.__messages: List[Message] = list()
        self.__sent: Set[Message] = set()
        self.__received: Set[Message] = set()
        self.__chatting_peer = Peer(peer_addr, False)

    def add_message(self, message, sender: bool):
        """
        Adds the given mag to the list of conversation messages
        :param sender: Determines if the owner of this conversation sent the mag or not
        :param message: Message to be added, could be of any type derived from Message
        """

        if isinstance(message, GreetingMessage):
            if not message.wants_to_talk:
                self._state = ConversationState.CLOSED
            else:
                # Only two variables remain, is_ack and sender
                if (not sender and message.ack) or (sender and message.ack):
                    self._state = ConversationState.ACTIVE
                elif sender and not message.ack:
                    self._state = ConversationState.AWAIT
                else:
                    self._state = ConversationState.INACTIVE
        elif isinstance(message, FarewellMessage):
            self._state = ConversationState.CLOSED

        self.__messages.append(message)

    def get_state(self):
        return self._state

    def expecting_types(self) -> Set[MessageType]:
        if self._state is ConversationState.INACTIVE:
            return {MessageType.GREETING}
        elif self._state is ConversationState.AWAIT:
            return {MessageType.GREETING}
        elif self._state is ConversationState.ACTIVE:
            return {MessageType.CHAT, MessageType.FAREWELL}
        elif self._state is ConversationState.CLOSED:
            return set()

    def get_connected_addr(self) -> (str, int):
        return self.__chatting_peer.address

    def get_peer_username(self) -> (str, int):
        return self.__chatting_peer.username

    def get_peer_color(self) -> (str, int):
        return self.__chatting_peer.color

    def set_connected_addr(self, addr: (str, int)):
        self.__chatting_peer.set_address(addr)

    def set_username(self, username: str):
        self.__chatting_peer.set_username(username)

    def set_color(self, color: str):
        self.__chatting_peer.set_color(color)
