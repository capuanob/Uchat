from typing import Optional

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColorConstants
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QStackedWidget, QListWidget, \
    QFrame, QListWidgetItem, QListView, QErrorMessage

from Uchat.client import Client
from Uchat.helper.booter import BootThread
from Uchat.helper.colorScheme import load_themed_icon
from Uchat.helper.logger import DataType, get_file_path
from Uchat.model.account import Account
from Uchat.peer import Peer
from Uchat.ui.accountCreation import AccountCreationPresenter
from Uchat.ui.friends.PeerViews import FriendsListView, ConversationsListView
from Uchat.ui.main.ConversationView import ConversationView


class LandingWindow(QWidget):
    def __init__(self, parent: Optional[QWidget], account: Optional[Account], client: Client):
        super(QWidget, self).__init__(parent)

        self.__client = client
        self.__layout_manager = QVBoxLayout(self)
        self._placeholder_frame = QFrame()

        # Introduce main view variables, as null optionals
        self._conversation_view: Optional[ConversationView] = None
        self.__friends_list: Optional[FriendsListView] = None
        self.__convs_list: Optional[ConversationsListView] = None
        self.__splitter: Optional[QSplitter] = None
        self.__boot_thread: Optional[BootThread] = None

        if account:
            self.load_main_view(account)

            # Connect signals to slots
            self.__client.chat_received_signal.connect(self.handle_chat_received)
        else:
            self.account_creation = AccountCreationPresenter(self)
            self.__layout_manager.addWidget(self.account_creation)

            # Connect signals to slots
            self.account_creation.should_load_main_app.connect(self.load_main_view)

    def __del__(self):
        # FIXME: Deletion isnt working due to QThread throwing an exception on early termination
        pass

    def load_main_view(self, account: Account):
        self.__friends_list = FriendsListView(self, self.__client)
        self.__convs_list = ConversationsListView(self, self.__client)
        self._placeholder_frame = QFrame()

        self.__splitter = QSplitter(Qt.Horizontal)

        self.__boot_thread = BootThread(self, account)
        self.__boot_thread.upnp_exception_raised.connect(self.handle_upnp_exception)
        self.__boot_thread.start()

        self.__build_main_view()

    def __build_main_view(self):
        # Set up left-side of splitter

        # Stack of left-side widgets
        stack = QStackedWidget(self)

        conversation_list_widget = QFrame()
        conv_layout = QHBoxLayout(conversation_list_widget)
        conv_layout.addWidget(self.__convs_list)

        stack.addWidget(self.__friends_list)
        stack.addWidget(self.__convs_list)

        stack_labels = QListWidget(self)
        stack_labels.setViewMode(QListView.IconMode)
        stack_labels.setFixedWidth(55)
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

        self.__splitter.addWidget(left_frame)
        self.__splitter.addWidget(self._placeholder_frame)

        self.__layout_manager.addWidget(self.__splitter)

        # Connect events
        self.__client.start_chat_signal.connect(self.chat_started)

    # SLOTS

    @QtCore.pyqtSlot(Peer)
    def chat_started(self, peer: Peer):
        """

        :return:
        """
        peer.has_unread(False)
        self.__convs_list.model().add_peer(peer)
        self._conversation_view = ConversationView(self, self.__client,
                                                   peer, self.__friends_list.model(), self.__convs_list.model())
        self.layout()
        self.__splitter.replaceWidget(1, self._conversation_view)

    @QtCore.pyqtSlot(Peer)
    def handle_chat_received(self, peer: Peer):
        """
        Slot connected to client's chat_received_signal
        Used to alert the user of an incoming message when it is not for the current conversation
        :return:
        """
        if not self._conversation_view:
            return

        if peer is not self._conversation_view.peer():
            # The active conversation is different than the one receiving the message
            peer.has_unread(True)

    @QtCore.pyqtSlot(int, str)
    def handle_upnp_exception(self, err_code: int, err_msg: str):
        """
        Slot connected to BootThread's upnp_exception_raised signal
        Given a UPnP error, notifies the user through an error dialog.

        :param err_code: Error code associated with error
        :param err_msg: Error message raised
        """
        error_msg = QErrorMessage(self.__app)
        error_msg.showMessage("Error {}: {}".format(err_code, err_msg))
