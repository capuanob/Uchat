"""
Defines pop-ups necessary to facilitate full-functionality for the friends list
"""

from typing import Optional, Tuple

from PyQt5.QtWidgets import QDialog, QWidget, QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout

from Uchat.helper.globals import LISTENING_PORT
from Uchat.helper.validators import is_valid_ipv4, is_valid_port
from Uchat.peer import Peer


class AddFriendDialog(QDialog):
    """
    Pop-up used to get the IP and port of a new friend
    """

    def __init__(self, parent: Optional[QWidget], search_bar_text: str):
        super().__init__(parent)

        self.setWindowTitle(" ")
        self.setStyleSheet(self.styleSheet() +
                           "font-size: 15px;"
                           )
        self._layout_manager = QFormLayout(self)

        self._ip_field = QLineEdit()
        self._port_field = QLineEdit()
        self._submit_btn = QPushButton("Add")

        # Connect events
        self._submit_btn.clicked.connect(self._submit_button_pressed)

        self._setup_ui(search_bar_text)

    def _setup_ui(self, search_bar_text: str):
        """
        Sets up view
        """

        # Set placeholder texts
        self._ip_field.setPlaceholderText("ex. 172.16.254.1")

        # Set texts
        if is_valid_ipv4(search_bar_text):
            self._ip_field.setText(search_bar_text)
        self._port_field.setText(str(LISTENING_PORT))

        self._layout_manager.addRow("Friend's IPv4", self._ip_field)
        self._layout_manager.addRow("Friend's Port", self._port_field)
        self._layout_manager.addRow("", self._submit_btn)

    def _submit_button_pressed(self):
        """
        Handles dialog's return value based off form validity
        :return:
        """

        if is_valid_ipv4(self._ip_field.text()) and is_valid_port(self._port_field.text()):
            self.accept()

    def new_friend(self) -> Peer:
        """
        Generates a new peer using form data
        :exception: Will throw a valueError if this function isn't called on a validated dialog
        :return: the new peer
        """

        return Peer((self._ip_field.text(), int(self._port_field.text())), False, self._ip_field.text())


class ConnectionRequestDialog(QDialog):
    """
    Polls a user on if they would like to accept an incoming conversation request
    """

    def __init__(self, parent: Optional[QWidget], remote_host: Tuple[str, int], username: Optional[str] = None):
        super().__init__(parent)

        self.setWindowTitle(" ")
        self.setStyleSheet(self.styleSheet() +
                           "font-size: 15px;"
                           )

        self._remote_host = remote_host
        self._username = username
        self._layout_manager = QVBoxLayout(self)
        self._accept_btn = QPushButton("Accept")
        self._reject_btn = QPushButton("Reject")

        # Connect slots
        self._accept_btn.clicked.connect(lambda: self.accept())
        self._reject_btn.clicked.connect(lambda: self.reject())

        self._setup_ui()

    def _setup_ui(self):
        """
        Layout UI for display
        """
        ip, port = self._remote_host
        port = str(port)

        user_identifier = self._username if self._username else "{}:{}".format(ip, port)
        info_label = QLabel("Connection request received from: {}".format(user_identifier), self)

        self._layout_manager.addWidget(info_label)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._accept_btn)
        btn_layout.addWidget(self._reject_btn)

        self._layout_manager.addLayout(btn_layout)

