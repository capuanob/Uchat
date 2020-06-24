import socket
from sys import stdin
import selectors
from typing import Dict, Tuple

LISTENING_PORT: int = 49850  # Socket for a Uchat client to listen for incoming connections on

"""
Represents a client in the p2p network
Has the ability to send and receive messages to other clients
"""


class Client:
    def __init__(self, other_host):
        self.__listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create ipv4 TCP socket
        self.__address = ('', LISTENING_PORT)  # Address that is bindable to all available IPv4 interfaces on system
        self.__other_address = (other_host, LISTENING_PORT)

        # Store a mapping from a TCP socket's remote address to itself
        self.__chat_pack = Dict[Tuple[str, int], socket.socket]

        # Set up listening socket to listen on its address
        self.__listening_socket.bind(self.__address)  # Listen on this address
        self.__listening_socket.setblocking(False)
        self.__listening_socket.listen()

        print('Client listening on: {}'.format(self.__listening_socket.getsockname()))

    def send_message(self):
        """
        Gets a line of input from stdin and sends it to another client
        """

        # Get the message to be sent (standard input)
        message = stdin.readline()

        # TODO: Figure out how to differentiate multiple clients
        if self.__other_address not in self.__chat_pack:
            # Create a new TCP socket to communicate with other_address
            child_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            child_sock.connect(self.__other_address)
            self.__chat_pack[self.__other_address] = child_sock

        self.__chat_pack[self.__other_address].sendall(bytes(message, 'utf-8'))

    def get_message(self, comm_sock):
        """
        Reads all available bytes from a peer's socket and displays the message to stdout
        """

        # Read from listening socket
        data = comm_sock.recv(1024)  # TODO: Read entire buffer instead of arbitrary 1024
        print('From {}: {}'.format(comm_sock.getpeername(), data.decode('utf-8')), end='')

    def accept_connection(self, listening_sock, selector):
        """
        Accepts a new TCP connection to communicate with another client
        """

        new_sock, addr = listening_sock.accept()  # We must have had bound and listened to get here
        print('Accepting new connection from {}'.format(addr))
        selector.register(new_sock, selectors.EVENT_READ, data=None)  # Add to watched sockets
        self.get_message(new_sock)

    def handle_connection(self, updated_sock, selector):
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
