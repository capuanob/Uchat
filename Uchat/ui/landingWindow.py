from PyQt5.QtCore import QSize, Qt, QEvent, QObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from typing import Optional


class LandingWindow(QWidget):
    def __init__(self, parent: Optional[QWidget], has_account: bool):
        super(QWidget, self).__init__(parent)
        self.__layout_manager = QVBoxLayout(self)
        if has_account:
            self.__build_main_window()
        else:
            self.__build_account_creation_screen()

    def __build_account_creation_screen(self):
        """
        Screen to be shown to create a new account and save information to data directory
        """

        # Create top-widget, containing account creation form
        top_widget = QWidget(parent=self.parent())
        top_widget.setMinimumWidth(500)
        top_widget.setObjectName('create-account-top')
        top_widget_manager = QVBoxLayout(top_widget)

        welcome_lbl = QLabel('Welcome to UChat.', self)
        welcome_lbl.setObjectName('create-account-welcome')

        sub_lbl = QLabel('A secure and stateless, peer-to-peer messaging client')
        sub_lbl.setObjectName('sub-lbl')

        username_field = QLineEdit(top_widget)
        username_lbl = QLabel('USERNAME')

        self.color_field = QLineEdit('#', parent=top_widget)
        self.color_field.setInputMask('\#HHHHHH')
        self.color_field.textChanged.connect(self.profile_color_did_change)
        color_lbl = QLabel('PROFILE COLOR')
        create_btn = QPushButton("Create", parent=top_widget)
        create_btn.setObjectName('create-account-btn')

        # Layout top widget
        top_widget_manager.addWidget(welcome_lbl)
        top_widget_manager.addWidget(sub_lbl)
        top_widget_manager.addSpacing(15)
        top_widget_manager.addWidget(username_lbl)
        top_widget_manager.addWidget(username_field)
        top_widget_manager.addWidget(color_lbl)
        top_widget_manager.addWidget(self.color_field)
        top_widget_manager.addWidget(create_btn)
        top_widget_manager.addSpacing(30)

        # Layout landing window
        self.__layout_manager.addWidget(top_widget, alignment=Qt.AlignCenter)
        self.__layout_manager.addStretch()

    def __build_main_window(self):
        pass

    def profile_color_did_change(self, text: str):
        if len(text) == 4 or len(text) == 7:
            self.color_field.setStyleSheet('color: ' + text + ';')
        else:
            self.color_field.setStyleSheet('color: white;')
