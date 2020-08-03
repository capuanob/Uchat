import selectors
import socket
import sys
import threading

from Uchat.client import Client
from Uchat.peer import Peer
from Uchat.ui.application import Application

sel = selectors.DefaultSelector()

def poll_selector(client: Client):
    while True:
        try:
            events = sel.select(timeout=None)
            for key, mask in events:
                client.handle_connection(key.fileobj)
        except socket.error as e:
            client.destroy()


def run():
    # Handle debug vs normal operation set-up
    if len(sys.argv) > 1 and sys.argv[1] == 'DEBUG':
        # Set up for debugging mode
        other_host = ('127.0.0.1', int(sys.argv[4]))

        if int(sys.argv[3]) == 2500:
            info = Peer(('', int(sys.argv[3])), True, 'debug_dan', '#FAB')
            peer = Peer(other_host, False)
            peer.username(other_host[0])

            client = Client(sel, info, peer)
        else:
            info = Peer(('', int(sys.argv[3])), True, 'test_tom', '#BD2')
            peer = Peer(other_host, False)
            peer.username(other_host[0])
            client = Client(sel, info, peer)
    else:
        other_host = input("Enter peer's IPv4: ")
        info = Peer(('', int(sys.argv[3])), 'nokillz', '#FAB')
        peer = Peer(other_host, False)
        client = Client(sel, 'nokillz', '#FAB', other_host=other_host)

    network_thread = threading.Thread(target=poll_selector, args=(client,))
    network_thread.daemon = True
    network_thread.start()

    Application(client)
