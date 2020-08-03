import selectors
from typing import Optional, List

from Uchat.MessageContext import MessageContext
from Uchat.conversation import Conversation, ConversationState
from Uchat.helper.error import print_err
from Uchat.network.messages.message import GreetingMessage, ChatMessage, MessageType, FarewellMessage, Message
from Uchat.network.tcp import TcpSocket
from Uchat.peer import Peer

"""
Represents a client in the p2p network
Has the ability to send and receive messages to other clients
"""


class Client:
    def __init__(self, selector, info: Peer, peer: Peer):
        """
        Constructs a new client
        :param selector: Reference to selector used for I/O multiplexing
        :param info: Peer information pertaining to this user
        :param peer: Peer information pertaining to client engaged in this conversation
        """

        self._info = info
        self._peer = peer

        # Conversations that this client is a member of
        self.__conversations: List[Conversation] = list()

        self.__listening_socket = TcpSocket(self._info.address()[1])  # Create ipv4 TCP socket
        self.__selector = selector  # Reference to selector that is driving I/O multiplexing

        self.__listening_socket.listen()  # Set up listening socket to listen on its address
        self.__selector.register(self.__listening_socket, selectors.EVENT_READ, data=None)

    def create_conversation(self, comm_sock: Optional[TcpSocket]) -> Conversation:
        """
        Creates and returns a new conversation
        :param comm_sock: Socket used for sending and receiving in this conversation
        :return: the newly created conversation
        """
        conv = Conversation(None, self._info, self._peer, comm_sock)
        self.__conversations.append(conv)
        return conv

    def accept_connection(self, listening_sock: TcpSocket):
        """
        Accepts a new TCP connection to communicate with another client
        """
        new_sock = listening_sock.accept_conn()  # We must have had bound and listened to get here

        if new_sock:
            self.__selector.register(new_sock, selectors.EVENT_READ, data=len(self.__conversations) - 1)
            self.create_conversation(new_sock)
            print('Accepting new connection \n L {} to R {}'.format(new_sock.get_local_addr(),
                                                                    new_sock.get_remote_addr()))
            self.handle_receipt(len(self.__conversations) - 1, new_sock)
        else:
            print_err(2, "Unable to accept incoming connection\n")

    def handle_connection(self, updated_sock: TcpSocket):
        """
        Determine if the provided socket is a new connection or a previously accepted connection
        providing a new mag
        :return:
        """

        if updated_sock is self.__listening_socket:  # We have an incoming connection
            self.accept_connection(updated_sock)
        else:
            # Must be the socket of an existing conversation

            # Get conversation index from its selector's data field (as saved on creation)
            sel_key = self.__selector.get_key(updated_sock)
            conv_idx: int = sel_key.data

            self.handle_receipt(conv_idx, updated_sock)

    def destroy(self):
        """
        send_farewell: If the user is receiving a farewell, no need to send one back
        :return:
        """

        for conv_idx in range(len(self.__conversations)):
            self.send_farewell(conv_idx)
            self.__conversations[conv_idx].destroy()
            self.__listening_socket.free()

    # Message Handling

    def handle_greeting_receipt(self, conv_idx: int, msg):

        if conv := self.conversation(conv_idx):
            # Save user's information locally
            conv.peer().username(msg.username)
            conv.peer().color(msg.get_hex_code())
            # TODO Poll user for accept / decline

        # Send response
        print('Receiving greeting')

        if not msg.ack:
            self.send_greeting(conv_idx, True, True)

    def handle_greeting_response_receipt(self, conv_idx: int, msg):
        if conv := self.conversation(conv_idx):
            status = '' if msg.wants_to_talk else 'not'
            print('User has {} accepted your conversation!'.format(status))
        self.handle_greeting_receipt(conv_idx, msg)

    def handle_farewell_receipt(self, conv_idx: int):
        print("Receiving farewell")
        if conv := self.conversation(conv_idx):
            print('Receiving farewell')
            self.send_farewell(conv_idx)
            conv.destroy()

    def handle_chat_receipt(self, msg):
        # Eventually log this message and its sender information
        print(msg.message, end='\n')

    def handle_receipt(self, conv_idx: int, comm_sock: TcpSocket):
        if conv := self.conversation(conv_idx):
            msg = comm_sock.recv_message()
            pre_expecting_types = conv.expecting_types()

            # Construct message context
            context = MessageContext(msg, conv.peer())
            conv.add_message(context)

            if msg and msg.m_type in pre_expecting_types:
                if msg.m_type is MessageType.GREETING:
                    if msg.ack:
                        self.handle_greeting_response_receipt(conv_idx, msg)
                    else:
                        self.handle_greeting_receipt(conv_idx, msg)
                elif msg.m_type is MessageType.FAREWELL:
                    self.handle_farewell_receipt(conv_idx)
                elif msg.m_type is MessageType.CHAT:
                    self.handle_chat_receipt(msg)
                else:
                    print_err(3, "Handling unknown msg type: {}".format(msg.m_type))
            else:
                print_err(3, "Received unexpected message type")

    # Message sending
    def send_greeting(self, conv_idx: int, ack: bool, wants_to_talk: bool = True):
        """
        Used to send a greeting mag to the peer, as a means of starting the conversation
        """
        if conv := self.conversation(conv_idx):
            greeting = GreetingMessage(int(conv.personal().color(), 16), conv.personal().username(), ack, wants_to_talk)
            print('Sending greeting')
            self.send(conv_idx, greeting)

    def send_chat(self, conv_idx: int, chat_message: ChatMessage):
        """
        Gets a line of input from stdin and sends it to another client as a wrapped ChatMessage
        """
        if not self.conversation(conv_idx):
            self.create_conversation(None)

        if conv := self.conversation(conv_idx):
            if conv.state() is ConversationState.ACTIVE:
                # As we are in an active conversation, safe to create msg
                print('Sending chat')
                self.send(conv_idx, chat_message)
            elif conv.state() is ConversationState.INACTIVE:
                self.send_greeting(conv_idx, False)
            else:
                print_err(4, "Will not send {}... on {}.".format(chat_message.message[:10], conv.state()))

    def send_farewell(self, conv_idx: int):
        if conv := self.conversation(conv_idx):
            if conv.state() is ConversationState.ACTIVE:
                farewell_msg = FarewellMessage()
                self.send(conv_idx, farewell_msg)
            else:
                print_err(4, "Will not send farewell on {}".format(conv.state()))

    def send(self, conv_idx: int, message: Message):
        """
        Generic function, used to send bytes to the peer
        """

        if conv := self.conversation(conv_idx):
            message_bytes = message.to_bytes()
            other_address = conv.peer().address()

            if not conv.sock():
                # Create a new TCP socket to communicate with other_address
                child_sock = TcpSocket()

                if child_sock.connect(other_address):  # Could a connection be established?
                    # Full-duplex socket, must listen for incoming messages and use for sending new ones
                    self.__selector.register(child_sock, selectors.EVENT_READ, data=conv_idx)
                    conv.sock(child_sock)

            if send_sock := conv.sock():
                # Connection established and socket exists
                context = MessageContext(message, conv.personal())
                conv.add_message(context)

                send_sock.send_bytes(message_bytes)

    # Getters & Setters

    def conversation(self, conv_idx: int) -> Optional[Conversation]:
        if conv_idx < len(self.__conversations):
            return self.__conversations[conv_idx]
        return None
