from Uchat.network.tcp import TcpSocket
from sys import stdin
import selectors
from typing import Dict
LISTENING_PORT: int = 52789  # Socket for a Uchat client to listen for incoming connections on

"""
Represents a client in the p2p network
Has the ability to send and receive messages to other clients
"""


class Client:
    def __init__(self, selector, other_host: str = None, debug_l_port: int = LISTENING_PORT,
                 debug_other_addr: (str, int) = None):
        """
        Constructs a new client

        :param other_host: Remote address of client to communicate with
        :param selector: Reference to selector used for I/O multiplexing
        :param debug_l_port: Optional, used to specify a different listening port for local debugging
        """
        global LISTENING_PORT

        LISTENING_PORT = debug_l_port
        self.__listening_socket = TcpSocket(LISTENING_PORT)  # Create ipv4 TCP socket
        self.__other_address: (str, int) = debug_other_addr if debug_other_addr else (other_host, LISTENING_PORT)
        self.__selector = selector  # Reference to selector that is driving I/O multiplexing
        # Store a mapping from a TCP socket's remote address to itself
        self.__chat_pack: Dict[(int, str), TcpSocket] = dict()

        self.__listening_socket.listen()  # Set up listening socket to listen on its address
        self.__selector.register(self.__listening_socket, selectors.EVENT_READ, data=None)

    def send_message(self):
        """
        Gets a line of input from stdin and sends it to another client
        """

        # Get the message to be sent (standard input)
        message = stdin.readline()
        print('Sending to {}'.format(self.__other_address))
        # TODO: Figure out how to differentiate multiple clients
        if self.__other_address not in self.__chat_pack:
            # Create a new TCP socket to communicate with other_address
            child_sock = TcpSocket()
            child_sock.connect(self.__other_address)
            self.__selector.register(child_sock, selectors.EVENT_READ, data=None)
            self.__update_chat_pack(self.__other_address, child_sock)

        self.__chat_pack[self.__other_address].send_message(message)

    def get_message(self, comm_sock: TcpSocket):
        """
        Reads all available bytes from a peer's socket and displays the message to stdout
        """

        # Read from communication socket
        msg = comm_sock.recv_message()
        print('From {}: {}'.format(comm_sock.get_remote_addr(), msg), end='')

    def accept_connection(self, listening_sock: TcpSocket):
        """
        Accepts a new TCP connection to communicate with another client
        """

        new_sock = listening_sock.accept_conn()  # We must have had bound and listened to get here
        self.__selector.register(new_sock, selectors.EVENT_READ, data=None)  # Add to watched sockets
        self.__update_chat_pack(new_sock.get_remote_addr(), new_sock)
        self.__other_address = new_sock.get_remote_addr()
        print('Accepting new connection \n L {} to R {}'.format(new_sock.get_local_addr(), new_sock.get_remote_addr()))
        self.get_message(new_sock)

    def handle_connection(self, updated_sock: TcpSocket):
        """
        Determine if the provided socket is a new connection or a previously accepted connection
        providing a new message
        :return:
        """

        if updated_sock is self.__listening_socket:  # We have an incoming connection
            self.accept_connection(updated_sock)
        else:
            self.get_message(updated_sock)

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
