from enum import Enum
from typing import List, Set, Tuple

from Uchat.network.tcp import TcpSocket
from Uchat.ui.delegate import profilePhotoPixmap
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

    def __init__(self, parent: Optional[QObject], personal: Peer, peer: Peer, sock: Optional[TcpSocket]):
        """
        :param parent: Parent of object\
        :param sock: TCPSocket used for full-duplex communication in this conversation
        """
        super().__init__(parent)

        self._state: ConversationState = ConversationState.INACTIVE
        self.__ctrl_messages: List[MessageContext] = list()  # Tracks every non-chat message part of conversation
        self.__chat_messages: List[MessageContext] = list()  # Tracks every chat message part of conversation

        # TCP Socket used for communicating in this conversation, full-duplex
        self.__comm_sock: Optional[TcpSocket] = sock
        self.__personal = personal
        self.__peer = peer

    # Model overrides
    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        Display as many rows as there are chat messages in list of messages
        :param parent:
        :return:
        """
        rows = len(self.__chat_messages)
        return rows

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid() or index.row() >= len(self.__chat_messages):
            return QVariant()

        context = self.__chat_messages[index.row()]

        if role == Qt.DisplayRole:
            # Message bubble view
            return context.msg.message
        elif role == Qt.DecorationRole:
            # Profile photo view
            sender = self.__personal if context.is_sender else self.__peer
            username = sender.username()
            color = sender.color()
            return profilePhotoPixmap.build_pixmap(color, username)
        else:
            return QVariant()

    def add_message(self, context: MessageContext):
        """
        Adds the given mag to the list of conversation messages
        :param context: Message Context containing message and sender
        """

        message = context.msg

        if isinstance(message, ChatMessage):
            # UI should only be notified to update with chat messages
            insertion_idx = len(self.__chat_messages)
            self.beginInsertRows(QModelIndex(), insertion_idx, insertion_idx)
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
        else:
            return set()

    def state(self):
        return self._state

    def peer(self, new_peer: Optional[Peer] = None) -> Peer:
        if new_peer:
            self.__peer = new_peer
        return self.__peer

    def personal(self, new_personal: Optional[Peer] = None) -> Peer:
        if new_personal:
            self.__personal = new_personal
        return self.__personal

    def chat_message_contexts(self) -> List[MessageContext]:
        """
        :return: the contexts contained in the tracked chat message list
        """
        return self.__chat_messages

    def connected_addr(self, addr: Optional[Tuple[str, int]] = None) -> (str, int):
        return self.__chatting_peer.address(addr)

    def sock(self, new_sock: Optional[TcpSocket] = None) -> Optional[TcpSocket]:
        if new_sock:
            self.__comm_sock = new_sock
        return self.__comm_sock

    def destroy(self):
        """
        Closes and destroys this conversation's socket
        """
        self._state = ConversationState.CLOSED
        self.__comm_sock.free()
