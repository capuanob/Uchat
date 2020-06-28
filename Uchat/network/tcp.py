from __future__ import annotations
import socket


# TODO: ADD EXCEPTION HANDLING TO THESE FUNCTIONS

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
        self.__address = ('', port if port else 1)

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

    def send_message(self, message: str):
        """

        :param message: Contents to send via an already connected socket
        """
        self.__sock.sendall(bytes(message, 'utf-8'))

    def recv_message(self) -> str:
        """

        :return Receives all bytes from the socket's buffer and returns their representative string
        """
        buffer_contents = bytes()
        curr_read = bytes()

        while curr_read:
            curr_read = self.__sock.recv(4096)
            if curr_read:
                buffer_contents += curr_read

        return str(curr_read, "ascii")

    def accept_conn(self) -> TcpSocket:
        new_sock, addr = self.__sock.accept()
        print('Accepting new connection from {}'.format(addr))
        return TcpSocket(sock=new_sock)

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
        return self.__sock.getpeername()

    def free(self):
        """
        Used to unbind a TCP socket and free its port
        """
        self.__sock.shutdown(socket.SHUT_RDWR)  # Send FIN to peer
        self.__sock.close()  # Decrement the handle count by 1