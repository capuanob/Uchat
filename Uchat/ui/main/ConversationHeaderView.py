"""
Defines the header of a conversation view
"""
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFrame, QHBoxLayout


class ConversationHeaderView(QFrame):
    """
    Appears at the top of a selected conversationView, showing a quick overview of the conversation's status and
    participants
    """
    def __init__(self, parent: QObject):
        super().__init__(parent)

        self.setObjectName("conversation-header")
        
        # Properties
        self.__layout = QHBoxLayout(self)

        self.__setup_UI()

    def __setup_UI(self):
        """
        Defines the UI
        """
        self.setFixedHeight(30)
