import selectors
import sys
from Uchat.client import Client

sel = selectors.DefaultSelector()


def run():
    other_host = input("Enter peer's IPv4: ")

    # Set up selector for I/o multiplexing
    client = Client(other_host)
    sel.register(client.get_listening_socket(), selectors.EVENT_READ, data=None)
    sel.register(sys.stdin, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.fileobj is sys.stdin:
                client.send_message()
            else:  # Must be an updated socket
                client.handle_connection(key.fileobj, sel)
