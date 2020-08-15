"""
Establishes module's model
"""
from typing import Optional, List, Any

from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt, pyqtSignal, QSize
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QWidget

from Uchat.helper.logger import get_friends, DataType, FileName, write_list_to_data_file
from Uchat.peer import Peer
from Uchat.ui.delegate import profilePhotoPixmap


class PeerList(QAbstractListModel):
    """

    """

    def __init__(self, parent: Optional[QWidget], is_stateless: bool):
        super().__init__(parent)

        self.is_stateless = is_stateless
        self._peers: List[Peer] = get_friends() if not is_stateless else []  # Model containing all peers that are currently added

    def __del__(self):
        # Destructor
        if not self.is_stateless:
            write_list_to_data_file(DataType.USER, FileName.FRIENDS, self._peers)  # Overwrite friend's list

    # Model overrides
    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        Determines how many rows a view using this model should display
        :param parent: Irrelevant for 1D list, usually specifies which list in a grid to get the length of
        :return: number of rows
        """

        return len(self._peers)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        """
        Determines what to display for a row
        :param index: Index of row to set up
        :param role: Type of data at row currently being considered (display, decoration...)
        """

        if not index.isValid() or index.row() >= len(self._peers):
            return QVariant()

        friend = self._peers[index.row()]

        if role == Qt.DisplayRole:
            # Message bubble view
            return friend.username()
        elif role == Qt.DecorationRole:
            return profilePhotoPixmap.build_pixmap(friend.color(), friend.username())
        elif role == Qt.StatusTipRole:
            return "status"
        elif role == Qt.SizeHintRole:
            return QSize(100, 50)
        elif role == Qt.BackgroundRole:
            return QBrush(Qt.red)
        else:
            return QVariant()

    def add_peer(self, new_peer: Peer):
        """
        Adds a friend to the model and notifies view to display new friend
        :param new_peer: Friend to be added
        """

        if not list(filter((lambda p: p.address() == new_peer.address()), self._peers)):
            insertion_idx = len(self._peers)
            self.beginInsertRows(QModelIndex(), insertion_idx, insertion_idx)
            self._peers.append(new_peer)
            self.endInsertRows()

    def at(self, index: int) -> Optional[Peer]:
        """
        :param index: Index of peer
        :return: peer at index
        """
        if 0 <= index < len(self._peers):
            return self._peers[index]
        return None

    def peers(self):
        """
        Getter, please don't alter the list
        :return:
        """
        return self._peers

    def remove_at(self, index: int) -> Optional[Peer]:
        """
        If it exists, removes the peer at the given index
        :param index:
        :return:
        """

        if 0 <= index < len(self._peers):
            return self._peers.pop(index)
        return None
