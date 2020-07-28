from __future__ import annotations
import socket
import struct
from typing import Optional, Tuple

from Uchat.helper.error import print_err
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
        try:
            self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__sock.bind(self.__address)
            self.__sock.setblocking(False)
            self.__sock.listen()
            print('Client listening on: {}'.format(self.__address))
        except OSError as os_err:
            print_err(2, "Error raised on attempt to establish listening socket\n" + str(os_err))

    def connect(self, conn_addr):
        """
        Connects the tcp socket to a remote address

        :param conn_addr: Address of host to connect to
        """
        try:
            self.__sock.connect(conn_addr)
            print('New connection: \n L {} -> R {}'.format(self.get_local_addr(), self.get_remote_addr()))
        except InterruptedError as int_err:
            print_err(2, "Connection time-out. Failure to connect to host: {}\n".format(self.get_remote_addr()) +
                      str(int_err))
        except OSError as os_err:
            print_err(2, "Failure to connect to host: {}\n".format(self.get_remote_addr()) + str(os_err))

    def send_bytes(self, message: bytes):
        """

        :param message: Send provided bytes via an already connected socket
        """
        try:
            self.__sock.sendall(message)
        except OSError as os_err:
            print_err(2, "Failure to send {}... to peer\n".format(message[:10]) + str(os_err))

    def recv_message(self) -> Optional[Message]:
        try:
            message_len = struct.Struct('I').unpack(self.__sock.recv(4))[0]
            message_bytes = self.__sock.recv(message_len)
            message_type = MessageType(struct.Struct('B').unpack(message_bytes[:1])[0])

            # Parse bytes to rebuild mag
            if message_type is MessageType.GREETING:
                return GreetingMessage.from_bytes(message_bytes)
            elif message_type is MessageType.CHAT:
                return ChatMessage.from_bytes(message_bytes)
            elif message_type is MessageType.FAREWELL:
                return FarewellMessage.from_bytes()
            else:
                return None
        except struct.error as struct_err:
            print_err(3, "Unable to decode bytes on listening socket.\n" + str(struct_err))
        except OSError as os_err:
            print_err(2, "Unable to receive bytes on listening socket.\n" + str(os_err))

    def accept_conn(self) -> Optional[TcpSocket]:
        try:
            new_sock, addr = self.__sock.accept()
            return TcpSocket(port=addr[1], sock=new_sock)
        except OSError:
            return None

    def fileno(self) -> int:
        """
        Used to make TcpSocket conform to file-object type for use in selectors and file I/O operations

        :return: The file descriptor of the stream, as an integer
        """
        return self.__sock.fileno()

    # Getters and Setters

    def get_local_addr(self) -> Optional[Tuple[str, int]]:
        """
        :return: the socket name, associated with the socket's local address
        """
        try:
            return self.__sock.getsockname()
        except OSError as os_err:
            print_err(2, "Unable to get socket name\n" + str(os_err))
            return None

    def get_remote_addr(self) -> Optional[Tuple[str, int]]:
        """

        :return: the socket's peer name, associated with the socket's remote address
        """
        try:
            return self.__sock.getpeername()
        except OSError as os_err:
            print_err(2, "Unable to get peer name\n" + str(os_err))
            return None

    def free(self):
        """
        Used to unbind a TCP socket and free its port
        """
        try:
            self.__sock.shutdown(socket.SHUT_RDWR)  # Send FIN to peer
            self.__sock.close()  # Decrement the handle count by 1
        except OSError as os_err:
            print_err(2, "Unable to free socket.\n" + str(os_err))
