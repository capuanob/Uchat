"""
Sets forth how to view a user's information
"""
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QLineEdit, QVBoxLayout, QFormLayout, QHBoxLayout, QPushButton

from Uchat.peer import Peer
from Uchat.ui.main.ProfilePhotoView import ProfilePhotoView


class UserInfoView(QDialog):
    """
    This view is used to display information about a peer, whether it be a friend or the client
    """

    def __init__(self, parent: Optional[QWidget], peer: Peer):
        super().__init__(parent)
        self.setWindowTitle(" ")

        self.setStyleSheet(self.styleSheet() + "font-size: 12px;")

        self._peer = peer
        self._layout_manager = QVBoxLayout(self)
        self._pfp = ProfilePhotoView(self, peer.username(), peer.color())
        self._username_field = QLineEdit(peer.username())
        self._ipv4_field = QLineEdit(peer.address()[0])
        self._port_field = QLineEdit(str(peer.address()[1]))
        self._conv_btn = QPushButton("Chat")
        self._edit_btn = QPushButton("Edit")

        self._is_editable: bool = False
        self._text_fields = [self._username_field, self._ipv4_field, self._port_field]

        self._setup_ui()

    def _setup_ui(self):
        """
        Sets forth the UI's layout
        """

        [field.setDisabled(True) for field in self._text_fields]

        hor_layout = QHBoxLayout()

        _info_manager = QFormLayout()
        _info_manager.addRow("Username", self._username_field)
        _info_manager.addRow("IPv4", self._ipv4_field)
        _info_manager.addRow("TCP Port", self._port_field)

        hor_layout.addWidget(self._pfp, 0, Qt.AlignCenter | Qt.AlignLeft)
        hor_layout.addSpacing(10)
        hor_layout.addLayout(_info_manager)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._conv_btn)
        btn_layout.addWidget(self._edit_btn)

        self._layout_manager.addLayout(hor_layout)
        self._layout_manager.addLayout(btn_layout)

    def _handle_save_edit(self):
        """
        Event that toggles between editing and saving
        """

        if self.is_editable:
            # Save and disable fields

            # Validate username (length rule), IPv4, and port
            self._peer.username(self._username_field.us)
