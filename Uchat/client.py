import selectors
from typing import Optional, Dict

from PyQt5.QtCore import QObject, pyqtSignal

from Uchat.MessageContext import MessageContext
from Uchat.model.conversation import Conversation, ConversationState
from Uchat.helper.error import print_err
from Uchat.network.messages.message import GreetingMessage, ChatMessage, MessageType, FarewellMessage, Message
from Uchat.network.tcp import TcpSocket
from Uchat.peer import Peer

"""
Represents a client in the p2p network
Has the ability to send and receive messages to other clients
"""


class Client(QObject):

    # Signals a client can emit
    new_friend_added_signal = pyqtSignal(Peer)  # Emitted when a friend is added
    tcp_conn_received_signal = pyqtSignal(Peer, TcpSocket) # Emitted when a user needs to permit a new connection rqst
    start_chat_signal = pyqtSignal(Peer)

    def __init__(self, parent: Optional[QObject], selector, info: Peer):
        """
        Constructs a new client
        :param selector: Reference to selector used for I/O multiplexing
        :param info: Peer information pertaining to this user
        """
        super().__init__(parent)

        self._info = info

        # Conversations that this client is a member of
        self.__conversations: Dict[Peer, Conversation] = dict()  # TODO: Change to be a mapping between ipv4 and conv

        self.__listening_socket = TcpSocket(self._info.address()[1])  # Create ipv4 TCP socket
        self.__selector = selector  # Reference to selector that is driving I/O multiplexing

        self.__listening_socket.listen()  # Set up listening socket to listen on its address
        self.__selector.register(self.__listening_socket, selectors.EVENT_READ, data=None)

    def create_conversation(self, peer: Peer, comm_sock: Optional[TcpSocket]) -> Conversation:
        """
        Creates and returns a new conversation
        :param peer: Peer to contact
        :param comm_sock: Socket used for sending and receiving in this conversation
        :return: the newly created conversation
        """
        conv = Conversation(None, self._info, peer, comm_sock)
        self.__conversations[peer] = conv
        return conv

    def delete_conversation(self, peer: Peer):
        """
        Deletes an existing conversation associated with a peer

        :param peer: Peer to delete associated conversation of
        """

        if conv := self.__conversations.pop(peer, None):
            try:
                if self.__selector.get_key(conv.sock()):
                    self.__selector.unregister(conv.sock())
            except (KeyError, ValueError):
                pass

            conv.destroy()

    def poll_connection_accept(self, listening_sock: TcpSocket):
        """
        Conditionally accepts a new TCP connection to communicate with another client
        """
        new_sock = listening_sock.accept_conn()  # We must have had bound and listened to get here

        if new_sock:
            new_peer = Peer(new_sock.get_remote_addr(), False, new_sock.get_remote_addr()[0])
            self.create_conversation(new_peer, new_sock)
            # Poll for accept / decline
            self.tcp_conn_received_signal.emit(new_peer, new_sock)
        else:
            print_err(2, "Unable to accept incoming connection\n")

    def accept_connection(self, new_peer: Peer, new_sock: TcpSocket):
        """
        Handles a connection with an approved socket; adds to selector and creates a conversation
        :param new_peer: Peer that conversation will be initiated with
        :param new_sock: Good socket
        """

        self.__selector.register(new_sock, selectors.EVENT_READ, data=new_peer)

        print('Accepting new connection \n L {} to R {}'.format(new_sock.get_local_addr(),
                                                                new_sock.get_remote_addr()))

    def reject_connection(self, peer: Peer):
        """
        Closes a connection with a socket that the user does not want to allow to continue to be connected
        :param peer: Peer to reject
        """
        self.send_greeting(peer, True, False)
        self.delete_conversation(peer)

    def handle_connection(self, updated_sock: TcpSocket):
        """
        Determine if the provided socket is a new connection or a previously accepted connection
        providing a new mag
        :return:
        """

        if updated_sock is self.__listening_socket:  # We have an incoming connection
            self.poll_connection_accept(updated_sock)
        else:
            # Must be the socket of an existing conversation

            # Get conversation index from its selector's data field (as saved on creation)
            sel_key = self.__selector.get_key(updated_sock)
            peer: Peer = sel_key.data

            self.handle_receipt(peer, updated_sock)

    def destroy(self):
        """
        send_farewell: If the user is receiving a farewell, no need to send one back
        :return:
        """

        for peer in self.__conversations.keys():
            self.send_farewell(peer)

            self.delete_conversation(peer)
            self.__listening_socket.free()

    # Message Handling

    def handle_greeting_receipt(self, peer: Peer, msg):

        if conv := self.conversation(peer):
            # Save user's information locally
            conv.peer().username(msg.username)
            conv.peer().color(msg.get_hex_code())

        print('Receiving greeting')

        # Send peer to ConversationView
        self.start_chat_signal.emit(peer)

        # Send response
        if not msg.ack:
            self.send_greeting(peer, True, True)

    def handle_greeting_response_receipt(self, peer: Peer, msg):
        if conv := self.conversation(peer):
            status = '' if msg.wants_to_talk else 'not'
            print('User has {} accepted your conversation!'.format(status))

            if not msg.wants_to_talk:
                # Destroy sock
                self.delete_conversation(peer)

        if msg.wants_to_talk:
            self.handle_greeting_receipt(peer, msg)

    def handle_farewell_receipt(self, peer: Peer):
        print("Receiving farewell")
        if conv := self.conversation(peer):
            # Deregister from socket
            self.delete_conversation(peer)

    def handle_chat_receipt(self, msg):
        # Eventually log this message and its sender information
        print(msg.message, end='\n')

    def handle_receipt(self, peer: Peer, comm_sock: TcpSocket):
        if conv := self.conversation(peer):
            msg = comm_sock.recv_message()
            pre_expecting_types = conv.expecting_types()

            # Construct message context
            context = MessageContext(msg, conv.peer())
            conv.add_message(context)

            if msg and msg.m_type in pre_expecting_types:
                if msg.m_type is MessageType.GREETING:
                    if msg.ack:
                        self.handle_greeting_response_receipt(peer, msg)
                    else:
                        self.handle_greeting_receipt(peer, msg)
                elif msg.m_type is MessageType.FAREWELL:
                    self.handle_farewell_receipt(peer)
                elif msg.m_type is MessageType.CHAT:
                    self.handle_chat_receipt(msg)
                else:
                    print_err(3, "Handling unknown msg type: {}".format(msg.m_type))
            else:
                print_err(3, "Received unexpected message type")

    # Message sending
    def send_greeting(self, peer: Peer, ack: bool, wants_to_talk: bool = True):
        """
        Used to send a greeting mag to the peer, as a means of starting the conversation
        """
        if conv := self.conversation(peer):
            greeting = GreetingMessage(int(conv.personal().color(), 16), conv.personal().username(), ack, wants_to_talk)
            print('Sending greeting')
            self.send(peer, greeting)

    def send_chat(self, peer: Peer, chat_message: ChatMessage):
        """
        Gets a line of input from stdin and sends it to another client as a wrapped ChatMessage
        """
        if conv := self.conversation(peer):
            if conv.state() is ConversationState.ACTIVE:
                # As we are in an active conversation, safe to create msg
                print('Sending chat')
                self.send(peer, chat_message)
            else:
                print_err(4, "Will not send {}... on {}.".format(chat_message.message[:10], conv.state()))
        else:
            print_err(4, "Conversation does not yet exist.")

    def send_farewell(self, peer: Peer):
        if conv := self.conversation(peer):
            if conv.state() is not ConversationState.CLOSED:
                print("Sending farewell")
                farewell_msg = FarewellMessage()
                self.send(peer, farewell_msg)
            else:
                print_err(4, "Will not send farewell on {}".format(conv.state()))

    def send(self, peer: Peer, message: Message):
        """
        Generic function, used to send bytes to the peer
        """

        if conv := self.conversation(peer):
            message_bytes = message.to_bytes()
            other_address = conv.peer().address()

            if not conv.sock():
                # Create a new TCP socket to communicate with other_address
                child_sock = TcpSocket()

                if child_sock.connect(other_address):  # Could a connection be established?
                    # Full-duplex socket, must listen for incoming messages and use for sending new ones
                    self.__selector.register(child_sock, selectors.EVENT_READ, data=peer)
                    conv.sock(child_sock)

            if send_sock := conv.sock():
                # Connection established and socket exists
                context = MessageContext(message, conv.personal())
                conv.add_message(context)

                send_sock.send_bytes(message_bytes)

    # Getters & Setters

    def conversation(self, peer: Peer) -> Optional[Conversation]:
        return self.__conversations.get(peer)
