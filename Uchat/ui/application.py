import sys
from typing import Optional

from PyQt5.QtCore import QSize, QPoint, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from Uchat.client import Client
from Uchat.helper.booter import execute_closure_methods
from Uchat.helper.globals import WINDOW_TITLE
from Uchat.helper.logger import get_user_account_data
from Uchat.model.account import Account
from Uchat.ui.landingWindow import LandingWindow


def get_center_pos(widget: QWidget) -> QPoint:
    """
    Calculates and returns the center position of the primary screen, accounting for the widget's size
    :param widget: Widget to be centered within the primary screen
    :return: A QPoint, pointing to the origin of the screen's adjusted center
    """

    center_screen: QPoint = QApplication.desktop().availableGeometry().center()
    return center_screen - widget.rect().center()


class Application(QObject):
    """
    Represents entire Uchat application
    """

    def __init__(self, client: Client):
        super().__init__(None)

        self.app_dimensions = QSize(700, 700)
        self.__app = QApplication(sys.argv)
        self.__main_win = QMainWindow(parent=None)
        self.__client = client
        self.__account = get_user_account_data()

        # Connect signals
        self.__generate_window(self.__account)

    def __del__(self):
        self.__client.destroy()
        execute_closure_methods()

    def __generate_window(self, account: Optional[Account]):
        """
        Generate's the application and it's primary window. UI main
        :return: Application's exit code
        """

        with open('style/darkstyle.qss', 'r') as file:
            self.__app.setStyleSheet(file.read())

        QApplication.setApplicationDisplayName(WINDOW_TITLE)
        self.__main_win.setGeometry(0, 0, self.app_dimensions.height(), self.app_dimensions.width())

        if len(sys.argv) > 1 and sys.argv[1] != 'DEBUG':
            self.__main_win.move(get_center_pos(self.__main_win))
        self.__main_win.show()

        # Load central widget
        landing_window = LandingWindow(self.__main_win, account, self.__client)
        self.__main_win.setCentralWidget(landing_window)
        self.__main_win.setMenuBar(landing_window.menu_bar())

        sys.exit(self.__app.exec())

    def exec(self):
        """
        Exposes QApplication's exec functionality
        :return: Program return code
        """
        return self.__app.exec()

    def free(self):
        del self.__main_win

    def execute_boot_thread(self):
        self.__boot_thread.start()
