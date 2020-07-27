import selectors
from datetime import datetime
from sys import stdin
from typing import Dict

from Uchat.MessageContext import MessageContext
from Uchat.conversation import Conversation, ConversationState
from Uchat.network.messages.message import GreetingMessage, ChatMessage, MessageType, FarewellMessage, Message
from Uchat.network.tcp import TcpSocket
from Uchat.peer import Peer

LISTENING_PORT: int = 52789  # Socket for a Uchat client to listen for incoming connections on

"""
Represents a client in the p2p network
Has the ability to send and receive messages to other clients
"""


class Client:
    def __init__(self, selector, username: str, profile_hex_code: str, other_host: str = None,
                 debug_l_port: int = LISTENING_PORT, debug_other_addr: (str, int) = None):
        """
        Constructs a new client

        :param other_host: Remote address of client to communicate with
        :param selector: Reference to selector used for I/O multiplexing
        :param debug_l_port: Optional, used to specify a different listening port for local debugging
        """
        global LISTENING_PORT

        LISTENING_PORT = debug_l_port

        other_address: (str, int) = debug_other_addr if debug_other_addr else (other_host, LISTENING_PORT)
        self._info = Peer(('', LISTENING_PORT), True, username, profile_hex_code[1:])
        self._peer = Peer(other_address, False)

        # Set up conversation, with whom this chat is with
        self.__conversation = Conversation(None, self)

        self.__listening_socket = TcpSocket(LISTENING_PORT)  # Create ipv4 TCP socket
        self.__selector = selector  # Reference to selector that is driving I/O multiplexing

        # Store a mapping from a TCP socket's remote address to itself
        self.__chat_pack: Dict[(int, str), TcpSocket] = dict()

        self.__listening_socket.listen()  # Set up listening socket to listen on its address
        self.__selector.register(self.__listening_socket, selectors.EVENT_READ, data=None)

    def accept_connection(self, listening_sock: TcpSocket):
        """
        Accepts a new TCP connection to communicate with another client
        """

        new_sock = listening_sock.accept_conn()  # We must have had bound and listened to get here
        self.__selector.register(new_sock, selectors.EVENT_READ, data=None)  # Add to watched sockets
        self.__update_chat_pack(new_sock.get_remote_addr(), new_sock)
        self.__conversation.peer().address(new_sock.get_remote_addr())
        print('Accepting new connection \n L {} to R {}'.format(new_sock.get_local_addr(), new_sock.get_remote_addr()))
        self.handle_receipt(new_sock)

    def handle_connection(self, updated_sock: TcpSocket):
        """
        Determine if the provided socket is a new connection or a previously accepted connection
        providing a new mag
        :return:
        """

        if updated_sock is self.__listening_socket:  # We have an incoming connection
            self.accept_connection(updated_sock)
        else:
            self.handle_receipt(updated_sock)

    def __update_chat_pack(self, address: (str, int), socket: TcpSocket):
        """
        Stores a mapping from address to socket in the chat pack

        If the mapping is already defined, the existing socket is freed and replaced
        :param address: Remote address of socket to be stored
        :param socket: Socket object
        :return:
        """
        if address in self.__chat_pack:
            self.__chat_pack[address].free()
        self.__chat_pack[address] = socket

    def destroy(self):
        """

        :return:
        """
        self.__listening_socket.free()
        for addr, sock in self.__chat_pack.items():
            sock.free()

    # Message Handling

    def handle_greeting_receipt(self, msg):
        # Save user's information locally
        self.__conversation.peer().username(msg.username)
        self.__conversation.peer().color(msg.get_hex_code())
        # Poll user for accept / decline

        # Send response
        print('Receiving greeting')

        if not msg.ack:
            self.send_greeting(True, True)

    def handle_chat_receipt(self, msg):
        print('{}: {} says {}'.format(datetime.fromtimestamp(msg.time_stamp), self.__conversation.peer().username(),
                                      msg.message), end='')

    def handle_farewell_receipt(self):
        print('Receiving farewell')
        self.destroy()

    def handle_greeting_response_receipt(self, msg):
        status = '' if msg.acceptsConversation else 'not'
        print('User has {} accepted your conversation!'.format(status))

    def handle_receipt(self, comm_sock: TcpSocket):
        msg = comm_sock.recv_message()
        pre_expecting_types = self.__conversation.expecting_types()

        # Construct message context
        context = MessageContext(msg, self._peer)
        self.__conversation.add_message(context)

        if msg and msg.m_type in pre_expecting_types:
            if msg.m_type is MessageType.GREETING:
                self.handle_greeting_receipt(msg)
            elif msg.m_type is MessageType.CHAT:
                self.handle_chat_receipt(msg)
            elif msg.m_type is MessageType.FAREWELL:
                self.handle_farewell_receipt(msg)
            else:
                print('Handling unknown mag type: {}'.format(msg.m_type))
        else:
            print('Handling unexpected mag type: {}'.format(msg.m_type))

    # Message sending
    def send_greeting(self, ack: bool, wants_to_talk: bool = True):
        """
        Used to send a greeting mag to the peer, as a means of starting the conversation
        """
        greeting = GreetingMessage(int(self._info.color(), 16), self._info.username(), ack, wants_to_talk)
        print('Sending greeting')
        self.send(greeting)

    def send_chat(self, chat_message: ChatMessage):
        """
        Gets a line of input from stdin and sends it to another client as a wrapped ChatMessage
        """

        if self.__conversation.state() is ConversationState.ACTIVE:
            # As we are in an active conversation, safe to create mag
            print('Sending chat')
            self.send(chat_message)
        elif self.__conversation.state() is ConversationState.INACTIVE:
            self.send_greeting(False)
        else:
            print('Will not send {} on an {} conversation.'.format(chat_message.message, self.__conversation.state()))
            return

    def send_farewell(self):
        if self.__conversation.state() is ConversationState.ACTIVE:
            farewell_msg = FarewellMessage()
            self.send(farewell_msg)
            self.destroy()
        else:
            print('Will not send farewell on {} conversation state'.format(self.__conversation.state()))

    def send(self, message: Message):
        """
        Generic function, used to send bytes to the peer
        """
        message_bytes = message.to_bytes()

        context = MessageContext(message, self.__conversation.personal())
        self.__conversation.add_message(context)

        other_address = self.__conversation.peer().address()
        if other_address not in self.__chat_pack:
            # Create a new TCP socket to communicate with other_address
            child_sock = TcpSocket()
            child_sock.connect(other_address)
            self.__selector.register(child_sock, selectors.EVENT_READ, data=None)
            self.__update_chat_pack(other_address, child_sock)

        self.__chat_pack[other_address].send_bytes(message_bytes)

    # Getters & Setters

    def info(self) -> Peer:
        return self._info

    def peer(self) -> Peer:
        return self._peer

    def conversation(self):
        return self.__conversation