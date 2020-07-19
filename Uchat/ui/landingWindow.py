from typing import Optional, Set

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

from Uchat.MessageContext import DEBUG_MESSAGES
from Uchat.helper.logger import write_to_data_file, DataType, FileName
from Uchat.model.account import Account
from Uchat.ui.colorScheme import DarkModeColorScheme
from Uchat.ui.main.ChatAreaView import ChatAreaView
from Uchat.ui.main.ConversationView import ConversationView
from Uchat.ui.main.ProfilePhotoView import ProfilePhotoView


def validate_line_edit(widget: QLineEdit, validator) -> bool:
    if not widget.validator():
        print('%s does not have a validator!' % widget)
        return False

    state = widget.validator().validate(widget.text(), 0)[0]
    return state == validator.Acceptable


class LandingWindow(QWidget):
    def __init__(self, parent: Optional[QWidget], has_account: bool):
        super(QWidget, self).__init__(parent)

        self.__layout_manager = QVBoxLayout(self)
        self.widgets_with_errors: Set[QWidget] = set()

        if has_account:
            self.conversation_view: ChatAreaView = ChatAreaView(self, DEBUG_MESSAGES)
            # self.send_view: MessageSendView = MessageSendView(self)

            self.__build_main_window()
        else:
            self.username_field: QLineEdit = QLineEdit()
            self.color_field: QLineEdit = QLineEdit()
            self.create_btn: QPushButton = QPushButton()
            self.profile_photo_preview = ProfilePhotoView(self)

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

        profile_manager = QHBoxLayout()
        # Set up welcome labels and profile photo preview
        label_manager = QVBoxLayout()
        welcome_lbl = QLabel('Welcome to UChat.', self)
        welcome_lbl.setObjectName('create-account-welcome')
        profile_manager.addLayout(label_manager)
        profile_manager.addWidget(self.profile_photo_preview, 0, Qt.AlignRight | Qt.AlignVCenter)
        profile_manager.addSpacing(10)

        sub_lbl = QLabel('A secure and stateless, peer-to-peer messaging client')
        sub_lbl.setObjectName('sub-lbl')
        label_manager.addWidget(welcome_lbl)
        label_manager.addWidget(sub_lbl)

        self.username_field = QLineEdit(top_widget)
        # Only allow alphanumeric usernames between length 3 and 12
        self.username_field.setValidator(QRegExpValidator(QRegExp('[0-9a-zA-Z]{3,20}'), self.username_field))
        self.username_field.textChanged.connect(self.profile_photo_did_change)

        username_lbl = QLabel('USERNAME')

        self.color_field = QLineEdit('#', parent=top_widget)
        self.color_field.setInputMask('\#HHHHHH')
        self.color_field.textChanged.connect(self.profile_photo_did_change)
        color_lbl = QLabel('PROFILE COLOR')
        self.create_btn = QPushButton("Create", parent=top_widget)
        self.create_btn.setObjectName('create-account-btn')
        self.create_btn.clicked.connect(self.create_btn_pressed)

        # Layout top widget
        top_widget_manager.addLayout(profile_manager, 0)
        top_widget_manager.addSpacing(15)
        top_widget_manager.addWidget(username_lbl)
        top_widget_manager.addWidget(self.username_field)
        top_widget_manager.addWidget(color_lbl)
        top_widget_manager.addWidget(self.color_field)
        top_widget_manager.addWidget(self.create_btn)
        top_widget_manager.addSpacing(30)

        # Layout landing window
        self.__layout_manager.addWidget(top_widget, alignment=Qt.AlignCenter)
        self.__layout_manager.addStretch()

    def __build_main_window(self):
        self.__layout_manager.addWidget(ConversationView(self))

    # Event Handlers
    def profile_photo_did_change(self):
        self.remove_error_outline(self.sender())
        self.profile_photo_preview.update_label(self.username_field.text(), self.color_field.text())

    def create_btn_pressed(self):

        # Get validation state of forms
        is_valid_username = validate_line_edit(self.username_field, QRegExpValidator)

        hex_code = self.color_field.text()
        is_valid_hex_code = len(hex_code[1:]) == 3 or len(hex_code[1:]) == 6  # Account for leading # character

        if is_valid_username and is_valid_hex_code:
            # Save to global data log and proceed
            self.save_user_data()
        else:
            # Blink invalid fields red twice and add error msg to them
            if not is_valid_hex_code:
                self.outline_on_error(self.color_field)
            if not is_valid_username:
                self.outline_on_error(self.username_field)

    # Helper Functions
    def remove_error_outline(self, widget: QWidget):
        if widget in self.widgets_with_errors:
            widget.setStyleSheet('border-color: black')

    def outline_on_error(self, widget: QWidget):
        self.widgets_with_errors.add(widget)
        widget.setStyleSheet(
            'border-width: 1px; border-style: outset; border-color: %s;' % DarkModeColorScheme.error_red)

    # Data saving
    def save_user_data(self):
        user_data = Account(self.username_field.text(), self.color_field.text())
        write_to_data_file(DataType.USER, FileName.GLOBAL, user_data)
