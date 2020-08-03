from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from Uchat.client import Client
from Uchat.helper.logger import get_user_account_data, DataType, FileName
from Uchat.ui.landingWindow import LandingWindow

import sys


def get_center_pos(widget: QWidget) -> QPoint:
    """
    Calculates and returns the center position of the primary screen, accounting for the widget's size
    :param widget: Widget to be centered within the primary screen
    :return: A QPoint, pointing to the origin of the screen's adjusted center
    """

    center_screen: QPoint = QApplication.desktop().availableGeometry().center()
    return center_screen - widget.rect().center()


class Application:
    """
    Represents entire Uchat application
    """
    def __init__(self, client: Client):
        self.app_dimensions = QSize(500, 500)
        self.__app = QApplication(sys.argv)
        self.__main_win = QMainWindow(parent=None)
        self.__main_win.closeEvent = self.__handle_program_exit
        self.__client = client

        self.__generate_window()

    def __generate_window(self):
        """
        Generate's the application and it's primary window. UI main
        :return: Application's exit code
        """

        with open('style/darkstyle.qss', 'r') as file:
            self.__app.setStyleSheet(file.read())

        self.__main_win.setWindowTitle('UChat - Secure P2P Messaging')
        self.__main_win.setGeometry(0, 0, self.app_dimensions.height(), self.app_dimensions.width())
        self.__main_win.move(get_center_pos(self.__main_win))
        self.__main_win.show()

        # Load central widget
        account = get_user_account_data()
        landing_window = LandingWindow(self.__main_win, account is not None, self.__client)
        self.__main_win.setCentralWidget(landing_window)

        sys.exit(self.__app.exec_())

    def __handle_program_exit(self, event: QCloseEvent):
        """
        Free socket and send farewell to partner
        """
        self.__client.destroy()
        QMainWindow.closeEvent(self.__main_win, event)
