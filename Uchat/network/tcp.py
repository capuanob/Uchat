from __future__ import annotations
import socket

# TODO: ADD EXCEPTION HANDLING TO THESE FUNCTIONS
from struct import Struct
from typing import Optional

from Uchat.network.messages.message import GreetingMessage, MessageType, Message, ChatMessage, FarewellMessage


class TcpSocket:
    """
    Abstraction upon python sockets
    Used to establish a new TCP connection over the internet
    """

    def __init__(self, port: int = None, sock: socket.socket = None):
        """
        Constructs a new TCP socket

        :param port: The port to bind the socket to. None
        """

        # Actual TCP socket being abstracted upon
        self.__sock = sock if sock else socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Address of socket; '' means the socket should bind to any appropriate interface
        self.__address = ('', port if port else self.__sock.getsockname()[1])

    def listen(self):
        """
        Binds the socket to its address and listens for incoming messages
        """
        self.__sock.bind(self.__address)
        self.__sock.setblocking(False)
        self.__sock.listen()
        print('Client listening on: {}'.format(self.__address))

    def connect(self, conn_addr):
        """
        Connects the tcp socket to a remote address

        :param conn_addr: Address of host to connect to
        """
        self.__sock.connect(conn_addr)
        print('New connection: \n L {} -> R {}'.format(self.get_local_addr(), self.get_remote_addr()))

    def send_bytes(self, message: bytes):
        """

        :param message: Send provided bytes via an already connected socket
        """
        self.__sock.sendall(message)

    def recv_greeting(self, greeting: bytes) -> GreetingMessage:
        """

        :return Receives all bytes from the socket's buffer and returns their representative string
        """
        greeting_message = GreetingMessage.from_bytes(greeting)

        return greeting_message

    def recv_message(self) -> Optional[Message]:
        message_len = Struct('I').unpack(self.__sock.recv(4))[0]
        message_bytes = self.__sock.recv(message_len)
        message_type = MessageType(Struct('B').unpack(message_bytes[:1])[0])

        # Parse bytes to rebuild mag
        if message_type is MessageType.GREETING:
            return GreetingMessage.from_bytes(message_bytes)
        elif message_type is MessageType.CHAT:
            return ChatMessage.from_bytes(message_bytes)
        elif message_type is MessageType.FAREWELL:
            return FarewellMessage.from_bytes()
        else:
            return None

    def accept_conn(self) -> TcpSocket:
        new_sock, addr = self.__sock.accept()
        return TcpSocket(port=addr[1], sock=new_sock)

    def fileno(self) -> int:
        """
        Used to make TcpSocket conform to file-object type for use in selectors and file I/O operations

        :return: The file descriptor of the stream, as an integer
        """
        return self.__sock.fileno()

    # Getters and Setters

    def get_local_addr(self):
        """
        :return: the socket name, associated with the socket's local address
        """
        return self.__sock.getsockname()

    def get_remote_addr(self):
        """

        :return: the socket's peer name, associated with the socket's remote address
        """
        try:
            return self.__sock.getpeername()
        except socket.error as e:
            return None

    def free(self):
        """
        Used to unbind a TCP socket and free its port
        """
        self.__sock.shutdown(socket.SHUT_RDWR)  # Send FIN to peer
        self.__sock.close()  # Decrement the handle count by 1
