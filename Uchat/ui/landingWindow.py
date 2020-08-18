from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegExpValidator, QColorConstants
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QSplitter, QStackedWidget, QListWidget, \
    QFrame, QListWidgetItem, QListView

from Uchat.client import Client
from Uchat.helper.colorScheme import load_themed_icon
from Uchat.helper.logger import write_to_data_file, DataType, FileName, get_file_path
from Uchat.model.account import Account
# from Uchat.network.upnp import ensure_port_is_forwarded
from Uchat.peer import Peer
from Uchat.ui.accountCreation import AccountCreationPresenter
from Uchat.ui.friends.friendsListView import FriendsListView, ConversationsListView
from Uchat.ui.main.ConversationView import ConversationView

class LandingWindow(QWidget):
    def __init__(self, parent: Optional[QWidget], has_account: bool, client: Client):
        super(QWidget, self).__init__(parent)

        self.__layout_manager = QVBoxLayout(self)
        self.__client = client

        if has_account:
            self.__friends_list = FriendsListView(self, client)
            self.__convs_list = ConversationsListView(self, client)
            self._placeholder_frame = QFrame()
            self._conversation_view = None

            self.splitter = QSplitter(Qt.Horizontal)

            self.__build_main_view()
        else:
            self.__layout_manager.addWidget(AccountCreationPresenter(self))

    def __build_main_view(self):
        # Set up left-side of splitter

        # Stack of left-side widgets
        stack = QStackedWidget(self)

        stack.addWidget(self.__friends_list)
        stack.addWidget(self.__convs_list)

        stack_labels = QListWidget(self)
        stack_labels.setViewMode(QListView.IconMode)
        stack_labels.setFixedWidth(50)
        stack_labels.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        stack_labels.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add friend icon

        friend_fp = str(get_file_path(DataType.ICONS, file_name_str="user.svg"))
        friend_icon = load_themed_icon(friend_fp, QColorConstants.White)
        stack_labels.addItem(QListWidgetItem(friend_icon, None, stack_labels, 0))

        # Add chat icon
        chat_fp = str(get_file_path(DataType.ICONS, file_name_str="comment.svg"))
        chat_icon = load_themed_icon(chat_fp, QColorConstants.White)
        stack_labels.addItem(QListWidgetItem(chat_icon, None, stack_labels, 0))

        stack_labels.currentRowChanged.connect(lambda i: stack.setCurrentIndex(i))

        # Combine stack and labels in frame
        left_frame = QFrame()
        layout_manager = QHBoxLayout(left_frame)
        layout_manager.addWidget(stack_labels)
        layout_manager.addWidget(stack)

        self.splitter.addWidget(left_frame)
        self.splitter.addWidget(self._placeholder_frame)

        self.__layout_manager.addWidget(self.splitter)

        # Connect events
        self.__client.start_chat_signal.connect(self.chat_started)

    def chat_started(self, peer: Peer):
        """

        :return:
        """
        self.__convs_list.model().add_peer(peer)
        self._conversation_view = ConversationView(self, self.__client,
                                                   peer, self.__friends_list.model(), self.__convs_list.model())
        self.layout()
        self.splitter.replaceWidget(1, self._conversation_view)

