from enum import Enum
from typing import List, Set, Tuple

from typing import Optional, Any
from PyQt5.QtCore import QObject, QAbstractListModel, QModelIndex, QVariant, Qt

from Uchat.MessageContext import MessageContext
from Uchat.network.messages.message import FarewellMessage, GreetingMessage, MessageType, ChatMessage
from Uchat.peer import Peer


class ConversationState(Enum):
    """
    If viewing a conversation as a Finite State Automata, this would be it's current state
    See docs for the respective FSM for reference
    """
    INACTIVE = 0  # Newly created conversation, no action has been taken by any participant
    AWAIT = 1  # A user has sent it's peer a greeting that has not yet been responded to
    ACTIVE = 2  # The requesting client ('requester') has received a conversation acceptance request, can now chat
    CLOSED = 3  # The conversation is permanently closed, whether to declination or a participant leaving after chatting


class Conversation(QAbstractListModel):
    """
    A conversation is held between two or more clients. A client can be engaged in multiple, simultaneous conversations.
    Responsible for tracking messages sent during current conversation, it's participants, and it's status
    """

    def __init__(self, parent: Optional[QObject], peer: Peer):
        super().__init__(parent)

        self._state: ConversationState = ConversationState.INACTIVE
        self.__ctrl_messages: List[MessageContext] = list()  # Tracks every non-chat message part of conversation
        self.__chat_messages: List[MessageContext] = list()  # Tracks every chat message part of conversation

        self.__chatting_peer = peer

    # Model overrides
    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        Display as many rows as there are chat messages in list of messages
        :param parent:
        :return:
        """
        rows =  len(self.__chat_messages)
        return rows

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid() or index.row() >= len(self.__chat_messages):
            return QVariant()

        if role == Qt.DisplayRole:
            # Message bubble view
            return self.__chat_messages[index.row()].msg.message
        elif role == Qt.DecorationRole:
            # Profile photo view
            return "HELLO"
        else:
            return QVariant()

    def add_message(self, context: MessageContext):
        """
        Adds the given mag to the list of conversation messages
        :param context: Message Context containing message and sender
        :param sender: Determines if the owner of this conversation sent the mag or not
        """

        message = context.msg

        if isinstance(message, ChatMessage):
            # UI should only be notified to update with chat messages
            insertionIdx = len(self.__chat_messages)
            self.beginInsertRows(QModelIndex(), insertionIdx, insertionIdx)
            self.__chat_messages.append(context)
            self.endInsertRows()
        else:
            # Handle all control messages
            if isinstance(message, GreetingMessage):
                if not message.wants_to_talk:
                    self._state = ConversationState.CLOSED
                else:
                    # Only two variables remain, is_ack and sender
                    if (not context.is_sender and message.ack) or (context.is_sender and message.ack):
                        self._state = ConversationState.ACTIVE
                    elif context.is_sender and not message.ack:
                        self._state = ConversationState.AWAIT
                    else:
                        self._state = ConversationState.INACTIVE
            elif isinstance(message, FarewellMessage):
                self._state = ConversationState.CLOSED

            self.__ctrl_messages.append(context)

    def expecting_types(self) -> Set[MessageType]:
        if self._state is ConversationState.INACTIVE:
            return {MessageType.GREETING}
        elif self._state is ConversationState.AWAIT:
            return {MessageType.GREETING}
        elif self._state is ConversationState.ACTIVE:
            return {MessageType.CHAT, MessageType.FAREWELL}
        elif self._state is ConversationState.CLOSED:
            return set()

    def state(self):
        return self._state

    def peer_username(self, username: Optional[str] = None) -> str:
        return self.__chatting_peer.username(username)

    def peer_color(self, color: Optional[str]) -> str:
        return self.__chatting_peer.color(color)

    def peer(self) -> Peer:
        return self.__chatting_peer

    def chat_message_contexts(self) -> List[MessageContext]:
        """
        :return: the contexts contained in the tracked chat message list
        """
        return self.__chat_messages

    def connected_addr(self, addr: Optional[Tuple[str, int]] = None) -> (str, int):
        return self.__chatting_peer.address(addr)


# DEBUGGING

__debug_conv = None


def debug_conversation():
    """
    == DEBUGGING ==
    :return: A singleton conversation for debugging purposes
    """
    global __debug_conv

    if not __debug_conv:
        debug_dan = Peer(('127.0.0.1', 61000), True, 'debug_dan', '#FAB')
        test_tom = Peer(('127.0.0.1', 52607), False, 'test_tom', '#AA1')

        __debug_conv = Conversation(None, test_tom)
        __debug_conv.add_message(MessageContext(GreetingMessage(4011, 'debug_dan', False), debug_dan))
        __debug_conv.add_message(MessageContext(GreetingMessage(20301, 'test_tom', True), test_tom))
        __debug_conv.add_message(MessageContext(ChatMessage("Hello from debug dan!"), debug_dan))
        __debug_conv.add_message(MessageContext(ChatMessage("Hello from test tom!"), test_tom))
        __debug_conv.add_message(MessageContext(ChatMessage("How are you, dan?"), test_tom))
        __debug_conv.add_message(
            MessageContext(ChatMessage("I am very well! I have been busy debugging many projects and going "
                                       "on long rants to provide multi-line text testing. You?"),
                           debug_dan))
        __debug_conv.add_message(
            MessageContext(ChatMessage("I have also been sending double texts by the way!"), debug_dan))
        __debug_conv.add_message(MessageContext(ChatMessage("Fantastic!"), test_tom))
        __debug_conv.add_message(MessageContext(ChatMessage("Quite. Alright goodbye!"), debug_dan))
        __debug_conv.add_message(MessageContext(FarewellMessage(), debug_dan))
        __debug_conv.add_message(MessageContext(FarewellMessage(), test_tom))

    return __debug_conv
