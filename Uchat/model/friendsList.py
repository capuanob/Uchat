"""
Establishes module's model
"""
from typing import Optional, List, Any

from PyQt5.QtCore import QAbstractListModel, QModelIndex, QVariant, Qt
from PyQt5.QtWidgets import QWidget

from Uchat.helper.logger import write_to_data_file, get_friends, DataType, FileName
from Uchat.peer import Peer


class FriendsList(QAbstractListModel):
    """

    """

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)
        self._friends: List[Peer] = get_friends()  # Model containing all peers that are currently added

    # Model overrides
    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        Determines how many rows a view using this model should display
        :param parent: Irrelevant for 1D list, usually specifies which list in a grid to get the length of
        :return: number of rows
        """

        return len(self._friends)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        """
        Determines what to display for a row
        :param index: Index of row to set up
        :param role: Type of data at row currently being considered (display, decoration...)
        """

        if not index.isValid() or index.row() >= len(self._friends):
            return QVariant()

        friend = self._friends[index.row()]

        if role == Qt.DisplayRole:
            # Message bubble view
            return friend.username()
        else:
            return QVariant()

    def add_friend(self, new_friend: Peer):
        """
        Adds a friend to the model and notifies view to display new friend
        :param new_friend: Friend to be added
        """

        insertion_idx = len(self._friends)
        self.beginInsertRows(QModelIndex(), insertion_idx, insertion_idx)
        self._friends.append(new_friend)
        self.endInsertRows()

        write_to_data_file(DataType.USER, FileName.FRIENDS, new_friend, True)  # Append new friend to stored list

    def at(self, index: int) -> Optional[Peer]:
        """
        :param index: Index of peer
        :return: peer at index
        """
        if 0 <= index < len(self._friends):
            return self._friends[index]
        return None

