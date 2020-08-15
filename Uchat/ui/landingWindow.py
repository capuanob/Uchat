from typing import Optional, Set

from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QIcon, QPixmap, QColor, QColorConstants
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QSplitter, QTabWidget, \
    QStackedWidget, QListWidget, QFrame, QListWidgetItem, QListView

from Uchat.client import Client
from Uchat.helper.colorScheme import load_themed_icon
from Uchat.helper.logger import write_to_data_file, DataType, FileName, get_file_path
from Uchat.model.account import Account
from Uchat.peer import Peer
from Uchat.ui.friends.friendsListView import FriendsListView, ConversationsListView
from Uchat.ui.main.ConversationView import ConversationView
from Uchat.ui.main.ProfilePhotoView import ProfilePhotoView


def validate_line_edit(widget: QLineEdit, validator) -> bool:
    if not widget.validator():
        print('%s does not have a validator!' % widget)
        return False

    state = widget.validator().validate(widget.text(), 0)[0]
    return state == validator.Acceptable


class LandingWindow(QWidget):
    def __init__(self, parent: Optional[QWidget], has_account: bool, client: Client):
        super(QWidget, self).__init__(parent)

        self.__layout_manager = QVBoxLayout(self)
        self.__client = client

        if has_account:
            self.__friends_list = FriendsListView(self, client)
            self.__convs_list = ConversationsListView(self, client)
            self._placeholder_frame = QFrame()
            self._conversation_view = None

            self.splitter = QSplitter(Qt.Horizontal)

            self.__build_main_view()
        else:
            self.widgets_with_errors: Set[QWidget] = set()
            self.username_field: QLineEdit = QLineEdit()
            self.color_field: QLineEdit = QLineEdit()
            self.create_btn: QPushButton = QPushButton()
            self.profile_photo_preview = ProfilePhotoView(self)

            self.__build_account_creation_screen()

    def __build_main_view(self):
        # Set up left-side of splitter

        # Stack of left-side widgets
        stack = QStackedWidget(self)

        stack.addWidget(self.__friends_list)
        stack.addWidget(self.__convs_list)

        stack_labels = QListWidget(self)
        stack_labels.setViewMode(QListView.IconMode)
        stack_labels.setFixedWidth(50)
        stack_labels.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        stack_labels.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add friend icon

        friend_fp = str(get_file_path(DataType.ICONS, file_name_str="user.svg"))
        friend_icon = load_themed_icon(friend_fp, QColorConstants.White)
        stack_labels.addItem(QListWidgetItem(friend_icon, None, stack_labels, 0))

        # Add chat icon
        chat_fp = str(get_file_path(DataType.ICONS, file_name_str="comment.svg"))
        chat_icon = load_themed_icon(chat_fp, QColorConstants.White)
        stack_labels.addItem(QListWidgetItem(chat_icon, None, stack_labels, 0))

        stack_labels.currentRowChanged.connect(lambda i: stack.setCurrentIndex(i))

        # Combine stack and labels in frame
        left_frame = QFrame()
        layout_manager = QHBoxLayout(left_frame)
        layout_manager.addWidget(stack_labels)
        layout_manager.addWidget(stack)

        self.splitter.addWidget(left_frame)
        self.splitter.addWidget(self._placeholder_frame)

        self.__layout_manager.addWidget(self.splitter)

        # Connect events
        self.__client.start_chat_signal.connect(self.chat_started)

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
        write_to_data_file(DataType.USER, FileName.GLOBAL, user_data, False)

    def chat_started(self, peer: Peer):
        """

        :return:
        """
        self.__convs_list.model().add_peer(peer)
        self._conversation_view = ConversationView(self, self.__client,
                                                   peer, self.__friends_list.model(), self.__convs_list.model())
        self.layout()
        self.splitter.replaceWidget(1, self._conversation_view)

