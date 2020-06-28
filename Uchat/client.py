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
    def __init__(self, other_host: str):
        self.__listening_socket = TcpSocket(LISTENING_PORT)  # Create ipv4 TCP socket
        self.__other_address: (str, int) = (other_host, LISTENING_PORT)

        # Store a mapping from a TCP socket's remote address to itself
        self.__chat_pack: Dict[(int, str), TcpSocket] = dict()

        # Set up listening socket to listen on its address
        self.__listening_socket.listen()

    def send_message(self):
        """
        Gets a line of input from stdin and sends it to another client
        """

        # Get the message to be sent (standard input)
        message = stdin.readline()

        # TODO: Figure out how to differentiate multiple clients
        if self.__other_address not in self.__chat_pack:
            # Create a new TCP socket to communicate with other_address
            child_sock = TcpSocket()
            child_sock.connect(self.__other_address)
            self.__chat_pack[self.__other_address] = child_sock

        self.__chat_pack[self.__other_address].send_message(message)

    def get_message(self, comm_sock: TcpSocket):
        """
        Reads all available bytes from a peer's socket and displays the message to stdout
        """

        # Read from listening socket
        msg = comm_sock.recv_message()
        print('From {}: {}'.format(comm_sock.get_remote_addr(), msg), end='')

    def accept_connection(self, listening_sock: TcpSocket, selector):
        """
        Accepts a new TCP connection to communicate with another client
        """

        new_sock = listening_sock.accept_conn()  # We must have had bound and listened to get here
        selector.register(new_sock, selectors.EVENT_READ, data=None)  # Add to watched sockets
        self.get_message(new_sock)

    def handle_connection(self, updated_sock: TcpSocket, selector):
        """
        Determine if the provided socket is a new connection or a previously accepted connection
        providing a new message
        :return:
        """

        if updated_sock is self.__listening_socket:  # We have an incoming connection
            self.accept_connection(updated_sock, selector)
        else:
            self.get_message(updated_sock)

    # Getters and Setters

    def get_listening_socket(self):
        return self.__listening_socket
