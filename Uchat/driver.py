import selectors
import socket
import sys
import threading

from Uchat.client import Client
from Uchat.ui.application import Application

sel = selectors.DefaultSelector()


def poll_selector(client: Client):
    while True:
        try:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.fileobj is sys.stdin:
                    client.send_chat()
                else:  # Must be an updated socket
                    client.handle_connection(key.fileobj)
        except socket.error as e:
            client.destroy()

def run():

    # Handle debug vs normal operation set-up
    if len(sys.argv) > 1 and sys.argv[1] == 'DEBUG':
        # Set up for debugging mode
        other_host = ('127.0.0.1', int(sys.argv[4]))
        client = Client(sel, 'nokillz', '#FAB', debug_other_addr=other_host, debug_l_port=int(sys.argv[3]))
    else:
        other_host = input("Enter peer's IPv4: ")
        client = Client(sel, 'nokillz', '#FAB', other_host=other_host)

    network_thread = threading.Thread(target=poll_selector, args=(client,))
    network_thread.daemon = True
    network_thread.start()

    Application(client)



