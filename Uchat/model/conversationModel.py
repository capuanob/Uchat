from typing import Optional, List, Any
from PyQt5.QtCore import QAbstractListModel, QObject, QModelIndex, QVariant, Qt

from Uchat.MessageContext import MessageContext


class ConversationModel(QAbstractListModel):
    def __init__(self, contexts: List[MessageContext], parent: Optional[QObject]):
        super().__init__(parent)
        self.__contexts = contexts

    # Model Overrides
    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.__contexts)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid() or index.row() >= len(self.__contexts):
            return QVariant()
        elif role == Qt.DisplayRole:
            return self.__contexts[index.row()]
        else:
            return QVariant()