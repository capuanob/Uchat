"""
Defines the view for adding, removing, and interacting with friends
"""
from typing import Optional, List

from PyQt5.QtCore import QSize, QModelIndex, Qt, QPoint
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListView, QHBoxLayout, QLineEdit, QPushButton, QDialog, \
    QFrame, QMenu, QAbstractItemView, QAction

from Uchat.client import Client
from Uchat.helper.error import print_err
from Uchat.helper.globals import LISTENING_PORT
from Uchat.model.peerList import PeerList
from Uchat.network.tcp import TcpSocket
from Uchat.peer import Peer
from Uchat.ui.friends.friendDialogs import AddFriendDialog, ConnectionRequestDialog
from Uchat.ui.main.UserInfoDialog import UserInfoDialog


class PeerListView(QFrame):
    """"
    Abstract class, sets forth a basic list for viewing peers
    """

    def __init__(self, parent: Optional[QWidget], search_placeholder: str, is_stateless: bool):
        super().__init__(parent)

        self.setProperty("class", "friends_list")
        self._layout_manager = QVBoxLayout(self)
        self._header_manager = QHBoxLayout()

        # Set up search bar
        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText(search_placeholder)

        # Set up model
        self._peer_model = PeerList(self, is_stateless)
        self._peer_list_view = QListView(self)
        self._peer_list_view.setModel(self._peer_model)
        self._peer_list_view.setContextMenuPolicy(Qt.CustomContextMenu)

        # Connect events
        self._search_bar.returnPressed.connect(self._search_initiated)

        self._setup_ui()

    def _search_initiated(self):
        """
        Slot connected to returnPressed signal, initiates a search
        """
        print("Search!")

    def _setup_ui(self):
        """
        Establishes UI for display
        """

        # Set minimum width of search bar to length of placeholder text
        font_metrics = QFontMetrics(self._search_bar.font())
        txt_width = font_metrics.width(self._search_bar.placeholderText())
        self._search_bar.minimumSizeHint = QSize(txt_width, -1)
        self._search_bar.setFixedHeight(30)

        self._peer_list_view.setLayoutMode(QListView.Batched)  # Display as needed
        self._peer_list_view.setBatchSize(10)  # Number of messages to display
        self._peer_list_view.setFlow(QListView.TopToBottom)  # Display vertically
        self._peer_list_view.setResizeMode(QListView.Adjust)  # Items laid out every time view is resized

        # Set up header
        self._header_manager.addWidget(self._search_bar, 1)

        # Layout widgets
        self._layout_manager.addLayout(self._header_manager)
        self._layout_manager.addSpacing(10)
        self._layout_manager.addWidget(self._peer_list_view)
        self._layout_manager.setSpacing(0)

    def add_to_header(self, widget: QWidget):
        """
        Adds the given widget to the header
        :param widget: Widget to be added
        """
        self._header_manager.addSpacing(5)
        self._header_manager.addWidget(widget)

    def model(self) -> PeerList:
        """
        :return: The peer list model
        """
        return self._peer_model


class FriendsListView(PeerListView):
    """
    View that displays a list of all friends
    """

    def __init__(self, parent: Optional[QWidget], client: Client):
        super().__init__(parent, "Search for a friend...", False)

        self._client = client
        self.__add_btn = QPushButton('+')

        # Connect events
        self.__add_btn.clicked.connect(self._add_friend)
        self._peer_list_view.doubleClicked.connect(self._item_double_clicked)
        self._peer_list_view.customContextMenuRequested.connect(self.show_context_menu)
        self._client.new_friend_added_signal.connect(self.handle_new_friend_added)

        self.__setup_ui()

    def __setup_ui(self):
        """
        Establishes UI for display
        """

        # Set up button's height and width
        self.__add_btn.setMinimumSize(QSize(50, self._search_bar.height()))
        self.add_to_header(self.__add_btn)

    def _add_friend(self):
        """
        Generates a dialog for getting information needed to add a new friend
        """
        dialog = AddFriendDialog(self, self._search_bar.text())
        if dialog.exec() == QDialog.Accepted:
            self._peer_model.add_peer(dialog.new_friend())

    def handle_new_friend_added(self, new_friend: Peer):
        self._peer_model.add_peer(new_friend)

    def _item_double_clicked(self, index: QModelIndex):
        """
        Opens an editable info pane of the selected item
        :item: Index of selected item
        """

        friend = self._peer_model.at(index.row())
        if dialog := UserInfoDialog(self, friend):
            if dialog.exec() == QDialog.Accepted:  # Wants to chat
                # Find conversation with peer, if it already exists. Otherwise, create it
                if not self._client.conversation(friend):
                    self._client.create_conversation(friend, None)
                    self._client.send_greeting(friend, False)

    def show_context_menu(self, pos: QPoint):
        """

        :param pos:
        :return:
        """

        index = self._peer_list_view.indexAt(pos)

        if index.row() != -1:
            globalPos = self._peer_list_view.mapToGlobal(pos)

            # Have to specify QAction parent explicitly due to anti-pattern where it isn't done auto
            # Prevents FriendsListView from being garbage collected, so no save
            del_action = QAction("Delete")
            del_action.triggered.connect(lambda: self._peer_model.remove_at(index.row()))

            menu = QMenu(self)
            menu.addAction(del_action)
            # TODO: menu.addAction("Chat", self.)

            menu.exec(globalPos)
            del menu


class ConversationsListView(PeerListView):
    """
    View for viewing active conversations
    """

    def __init__(self, parent: Optional[QWidget], client: Client):
        super().__init__(parent, "Search for a conversation...", True)

        self._client = client

        # Connect events
        self._client.tcp_conn_received_signal.connect(self.poll_user_on_new_conversation)
        self._peer_list_view.doubleClicked.connect(self.show_conversation)
        self._peer_list_view.customContextMenuRequested.connect(self.show_context_menu)

    def poll_user_on_new_conversation(self, peer: Peer, sock: TcpSocket):
        """
        Ask the user if they would like to engage in a conversation with the sock's IP
        If so, accept connection. Otherwise, reject.

        :param peer: Peer requesting communication
        :param sock: Socket requesting to establish a conversation with this client
        """
        # Determine if remote host is already known
        remote_addr = sock.get_remote_addr()

        username = None
        if matching_friends := list(
                filter(lambda friend: friend.ipv4() == remote_addr[0], self._peer_model.peers())):
            username = matching_friends[0].__username()

        # Show dialog about new connection request
        dialog = ConnectionRequestDialog(self, remote_addr, username)

        if dialog.exec() == QDialog.Accepted:
            # If approved, add to friends list and accept
            self._peer_model.add_peer(peer)
            self._client.accept_connection(peer, sock)
        else:
            # Otherwise, reject
            self._client.reject_connection(peer)

    def show_conversation(self, index: QModelIndex):
        """
        On double click, show the conversation of the associated peer
        :param index:
        :return:
        """

        friend = self._peer_model.at(index.row())

        if self._client.conversation(friend):
            self._client.start_chat_signal.emit(friend)  # FIXME: Here
        else:
            print_err(4, "No conversation exists!")

    def show_context_menu(self, pos: QPoint):
        """
        Shows a context menu for a right-click on the list view
        :param pos: Position of user's click
        """

        index = self._peer_list_view.indexAt(pos)
        if index.row() != -1:
            globalPos = self._peer_list_view.mapToGlobal(pos)

            menu = QMenu(self)
            menu.addAction("Add", lambda: self.add_conversation_peer_to_friends(index))
            menu.addAction("Leave", lambda: self.__handle_leave_conversation(index))
            menu.exec(globalPos)

    def add_conversation_peer_to_friends(self, index: QModelIndex):
        """
        Adds sender of selected conversation to friends, using their listening port rather than conversation port
        """
        peer = self._peer_model.at(index.row())
        peer.address((peer.address()[0], LISTENING_PORT))
        self._client.new_friend_added_signal.emit(peer)

    def __handle_leave_conversation(self, index: QModelIndex):
        if peer := self._peer_model.remove_at(index.row()):
            self._client.send_farewell(peer)
            self._client.delete_conversation(peer)
