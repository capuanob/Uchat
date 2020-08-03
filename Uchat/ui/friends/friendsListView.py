"""
Defines the view for adding, removing, and interacting with friends
"""
from typing import Optional

from PyQt5.QtCore import QSize, QModelIndex
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListView, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QDialog

from Uchat.model.friendsList import FriendsList
from Uchat.ui.friends.addFriendDialog import AddFriendDialog
from Uchat.ui.main.UserInfoView import UserInfoView


class FriendsListView(QWidget):
    """
    View that displays a list of all friends
    """

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        self._layout_manager = QVBoxLayout(self)
        self.add_btn = QPushButton('+')
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for a friend...")

        # Set up model
        self._friends_model = FriendsList(self)
        self._friends_list = QListView(self)
        self._friends_list.setModel(self._friends_model)

        # Connect events
        self.add_btn.clicked.connect(self._add_friend)
        self._friends_list.doubleClicked.connect(self.item_double_clicked)

        self.__setup_ui()


    def __setup_ui(self):
        """
        Establishes UI for display
        """

        # Set minimum width of search bar to length of placeholder text
        font_metrics = QFontMetrics(self.search_bar.font())
        txt_width = font_metrics.width(self.search_bar.placeholderText())
        self.search_bar.minimumSizeHint = QSize(txt_width, -1)
        self.search_bar.setFixedHeight(30)

        # Set up button's height and width
        self.add_btn.setMinimumSize(QSize(50, 30))

        self._friends_list.setLayoutMode(QListView.Batched)  # Display as needed
        self._friends_list.setBatchSize(10)  # Number of messages to display
        self._friends_list.setFlow(QListView.TopToBottom)  # Display vertically
        self._friends_list.setResizeMode(QListView.Adjust)  # Items laid out every time view is resized

        # Set up header
        friends_header = QHBoxLayout()
        friends_header.addWidget(self.search_bar, 1)
        friends_header.addWidget(self.add_btn)

        # Layout widgets
        self._layout_manager.addLayout(friends_header)
        self._layout_manager.addWidget(self._friends_list)

    def _add_friend(self):
        """
        Generates a dialog for getting information needed to add a new friend
        """
        dialog = AddFriendDialog(self, self.search_bar.text())
        if dialog.exec() == QDialog.Accepted:
            self._friends_model.add_friend(dialog.new_friend())

    def item_double_clicked(self, index: QModelIndex):
        """
        Opens an editable info pane of the selected item
        :item: Index of selected item
        """

        if dialog := UserInfoView(self, self._friends_model.at(index.row())):
            if dialog.exec() == QDialog.Accepted:
                pass