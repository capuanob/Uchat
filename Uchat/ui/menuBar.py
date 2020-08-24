"""
Horizontal menu bar across application's top
"""
from typing import Optional

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMenuBar, QMenu, QApplication, QDialog, QMessageBox, QVBoxLayout, QLabel

from Uchat.helper.globals import LISTENING_PORT
from Uchat.helper.logger import get_user_account_data
from Uchat.network.ip import get_external_ip
from Uchat.peer import Peer
from Uchat.ui.main.UserInfoDialog import UserInfoDialog


class MenuBar(QMenuBar):
    def __init__(self, parent: QObject):
        super().__init__(parent)

        # Lay out menu
        self.__menus = [FileMenu(self), ViewMenu(self)]

        self.addMenu(self.__menus[0])
        self.addMenu(self.__menus[1])

    def at_index(self, index: int) -> Optional[QMenu]:
        if 0 <= index < len(self.__menus):
            return self.__menus[index]
        else:
            return None


class FileMenu(QMenu):
    """
    File menu, with all of its options
    """
    application_quit_signal = pyqtSignal()

    def __init__(self, parent: QObject):
        super().__init__("File", parent)
        self.setSeparatorsCollapsible(True)

        # Add options
        self.addAction("Quit", self.handle_quit, QKeySequence.Quit)
        self.addSeparator()
        self.addAction("About", self.show_about, QKeySequence.HelpContents)
        self.addAction("Account", self.show_account_info, QKeySequence.WhatsThis)

    # Slots

    @QtCore.pyqtSlot()
    def handle_quit(self):
        """
        Closes application properly
        """
        self.application_quit_signal.emit()

    @QtCore.pyqtSlot()
    def show_account_info(self):
        """
        Used to show user's account details, to provide to a potential friend
        """
        account = get_user_account_data()
        user = Peer((get_external_ip(), LISTENING_PORT), True, account.username())
        account_dialog = UserInfoDialog(self, user)
        account_dialog.exec()

    @QtCore.pyqtSlot()
    def show_about(self):
        """
        Displays the about application window
        """
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About UChat")
        about_dialog.setFixedSize(200, 200)
        about_dialog.setText("UChat is a totally decentralized, secure peer-to-peer messaging solution for "
                             "privacy in an increasingly public world.\n\nDeveloped by nullptr.")
        about_dialog.exec()


class ViewMenu(QMenu):
    """
    Handles options belonging to the view menu
    """

    show_conversations_signal = pyqtSignal()
    show_friends_signal = pyqtSignal()

    def __init__(self, parent: QObject):
        super().__init__("View", parent)
        self.setSeparatorsCollapsible(True)

        # Set up options
        self.addAction("Friends", self.handle_view_friends, 'F2')
        self.addAction("Conversations", self.handle_view_conversations, 'F3')

    def handle_view_friends(self):
        """
        Shows friends tab
        """
        self.show_friends_signal.emit()

    def handle_view_conversations(self):
        """
        Shows conversations tab
        """
        self.show_conversations_signal.emit()
