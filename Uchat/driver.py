import selectors
import socket
import sys
import threading

from Uchat.client import Client
from Uchat.helper.globals import LISTENING_PORT
from Uchat.helper.logger import get_user_account_data
from Uchat.peer import Peer
from Uchat.ui.application import Application

sel = selectors.DefaultSelector()


def poll_selector(client: Client):
    while True:
        try:
            events = sel.select(timeout=None)
            for key, mask in events:
                client.handle_connection(key.fileobj)
        except socket.error:
            client.destroy()


def run():
    # Handle debug vs normal operation set-up
    if len(sys.argv) > 1 and sys.argv[1] == 'DEBUG':
        # Set up for debugging mode

        if int(sys.argv[3]) == 2500:
            info = Peer(('', int(sys.argv[3])), True, 'debug_dan', '#FAB')

            client = Client(None, sel, info)
        else:
            info = Peer(('', int(sys.argv[3])), True, 'test_tom', '#BD2')
            client = Client(None, sel, info)
    else:
        user_data = get_user_account_data()
        info = Peer(('', LISTENING_PORT), True, user_data.username() if user_data else "",
                    user_data.hex_code() if user_data else "")
        client = Client(None, sel, info)

    network_thread = threading.Thread(target=poll_selector, args=(client,))
    network_thread.daemon = True
    network_thread.start()

    Application(client)
