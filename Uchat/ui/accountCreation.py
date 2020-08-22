"""
Designs and lays out all the windows necessary to successfully create an account
"""
from abc import abstractmethod
from typing import Set

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, Qt, QRegExp, QSize, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QStackedWidget, QPushButton, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QLabel, \
    QCheckBox

from Uchat.helper.globals import LISTENING_PORT
from Uchat.helper.logger import write_to_data_file, FileName, DataType
from Uchat.model.account import Account
from Uchat.ui.main.ProfilePhotoView import ProfilePhotoView


class AccountCreationPresenter(QWidget):
    """
    Handles data-validation, saving, and transitions between frames
    """

    should_load_main_app = pyqtSignal(Account)  # Signal to reload LandingWindow

    def __init__(self, parent: QObject):
        super().__init__(parent)

        self.__layout_manager = QVBoxLayout(self)
        self.__slide_stack = QStackedWidget()  # Stores the various frames for creating an account
        self.__proceed_btn = QPushButton("Get Started")  # Changes to say next or finish, slide-depending

        # Connect events
        self.__proceed_btn.clicked.connect(self.__proceed_btn_was_clicked)
        self.__setup_ui()

    @QtCore.pyqtSlot()
    def __proceed_btn_was_clicked(self):
        curr_idx = self.__slide_stack.currentIndex()

        if curr_idx == 0 and self.__slide_stack.isHidden():
            # Get Started, must show
            self.__slide_stack.show()
            self.__proceed_btn.setText("Next")
        elif self.__slide_stack.currentWidget().is_valid():
            if curr_idx + 1 == self.__slide_stack.count() - 1:
                # Second to last slide\
                self.__proceed_btn.setText("Finish")
                self.__slide_stack.setCurrentIndex(curr_idx + 1)
            elif curr_idx == self.__slide_stack.count() - 1:
                # Last slide

                # Save account data to global
                account = Account()
                for i in range(self.__slide_stack.count()):
                    self.__slide_stack.widget(i).fill_account_details(account)
                write_to_data_file(DataType.USER, FileName.GLOBAL, account, False)

                # Port-forward, if approved
                self.hide()
                self.should_load_main_app.emit(account)

            else:
                self.__slide_stack.setCurrentIndex(curr_idx + 1)

    def __setup_ui(self):

        # Create frames and populate stack
        self.__slide_stack.addWidget(AccountDetailsFrame(self.__slide_stack))
        self.__slide_stack.addWidget(NetworkDetailsFrame(self.__slide_stack))
        self.__slide_stack.hide()

        # Set up welcome top-half
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_frame.setFrameShadow(QFrame.Raised)
        content_frame.setObjectName("create-account-top")
        content_layout = QVBoxLayout(content_frame)

        # # Create labels
        welcome_lbl = QLabel('Welcome to UChat.')
        welcome_lbl.setObjectName('create-account-welcome')
        sub_lbl = QLabel('A secure and stateless, peer-to-peer messaging client')
        sub_lbl.setObjectName('sub-lbl')
        #
        # # Create separation line
        line = QFrame()
        line.setFixedHeight(1)
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        # Configure proceed button
        self.__proceed_btn.setFixedSize(QSize(85, 35))

        # # Layout
        content_layout.addWidget(welcome_lbl)
        content_layout.addWidget(sub_lbl)
        content_layout.addSpacing(10)
        content_layout.addWidget(line)
        content_layout.addWidget(self.__slide_stack)

        self.__layout_manager.addWidget(content_frame)
        self.__layout_manager.addSpacing(35)
        self.__layout_manager.addWidget(self.__proceed_btn)
        self.__layout_manager.addStretch()


class CreationSlide(QFrame):
    """
    Abstract class to be inherited by account creation slides
    """

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self._error_red = "#ED4337"

    @abstractmethod
    def is_valid(self) -> bool:
        """
        Determines whether or not all of the slide's fields have been properly filled before proceeding
        :return: whether the parent can proceed to the next slide safely
        """

    @abstractmethod
    def fill_account_details(self, account: Account):
        """
        Using the form data for the given slide, adds any requisite information to the overall account object
        :param account: Account object to populate
        :return:
        """


def validate_line_edit(widget: QLineEdit, validator) -> bool:
    if not widget.validator():
        print('%s does not have a validator!' % widget)
        return False

    state = widget.validator().validate(widget.text(), 0)[0]
    return state == validator.Acceptable


class AccountDetailsFrame(CreationSlide):
    """
    Asks the user for a username and profile-color
    """

    def __init__(self, parent: QObject):
        super().__init__(parent)

        self.__layout_manager = QVBoxLayout(self)
        self.__widgets_with_errors: Set[QWidget] = set()
        self.__username_field: QLineEdit = QLineEdit(self)
        self.__color_field: QLineEdit = QLineEdit('#', parent=self)
        self.__profile_photo_preview = ProfilePhotoView(self)

        self.__setup_ui()

    def is_valid(self) -> bool:
        # Get validation state of forms
        is_valid_username = validate_line_edit(self.__username_field, QRegExpValidator)

        hex_code = self.__color_field.text()
        is_valid_hex_code = len(hex_code[1:]) == 3 or len(hex_code[1:]) == 6  # Account for leading # character

        if not (is_valid_username and is_valid_hex_code):
            # Blink invalid fields red twice and add error msg to them
            if not is_valid_hex_code:
                self.outline_on_error(self.__color_field)
            if not is_valid_username:
                self.outline_on_error(self.__username_field)

        return is_valid_username and is_valid_hex_code

    def fill_account_details(self, account: Account):
        account.username(self.__username_field.text())
        account.hex_code(self.__color_field.text())

    # Event Handlers
    @QtCore.pyqtSlot()
    def profile_photo_did_change(self):
        self.remove_error_outline(self.sender())
        self.__profile_photo_preview.update_label(self.__username_field.text(), self.__color_field.text())

    # Helper Functions
    def remove_error_outline(self, widget: QWidget):
        if widget in self.__widgets_with_errors:
            widget.setStyleSheet('border-color: black')

    def outline_on_error(self, widget: QWidget):
        self.__widgets_with_errors.add(widget)
        widget.setStyleSheet(
            'border-width: 1px; border-style: outset; border-color: %s;' % self._error_red)

    def __setup_ui(self):
        # Lays out UI

        profile_manager = QHBoxLayout()

        # Set up welcome labels and profile photo preview
        profile_manager.addWidget(self.__profile_photo_preview, 0, Qt.AlignRight | Qt.AlignVCenter)
        profile_manager.addSpacing(10)

        # Only allow alphanumeric usernames between length 3 and 12
        self.__username_field.setValidator(QRegExpValidator(QRegExp('[0-9a-zA-Z]{3,20}'), self.__username_field))
        self.__username_field.textChanged.connect(self.profile_photo_did_change)

        username_lbl = QLabel('USERNAME (3-20 chars)')

        self.__color_field.setInputMask('\#HHHHHH')
        self.__color_field.textChanged.connect(self.profile_photo_did_change)
        color_lbl = QLabel('PROFILE COLOR')

        # Layout top widget
        self.__layout_manager.addLayout(profile_manager, 0)
        self.__layout_manager.addSpacing(15)
        self.__layout_manager.addWidget(username_lbl)
        self.__layout_manager.addWidget(self.__username_field)
        self.__layout_manager.addWidget(color_lbl)
        self.__layout_manager.addWidget(self.__color_field)
        self.__layout_manager.addSpacing(30)


class NetworkDetailsFrame(CreationSlide):
    """
    Used to solicit network details from the user
    """

    def __init__(self, parent: QObject):
        super().__init__(parent)

        self.__layout_manager = QVBoxLayout(self)
        self.__upnp_checkbox = QCheckBox("Use UPnP")

        self.__setup_ui()

    def is_valid(self) -> bool:
        return True

    def fill_account_details(self, account: Account):
        account.upnp(self.__upnp_checkbox.checkState() == Qt.Checked)

    def __setup_ui(self):
        # Lays out UI

        # Configure description
        port_description_label = QLabel(
            "This service utilizes TCP port {} to accept incoming conversations. If you are behind a NAT or Firewall "
            "and would prefer to statically port-forward, please do so. Failure to open the specified port will result "
            "in conversation requests from peers outside your network being dropped.".format(LISTENING_PORT))
        port_description_label.setWordWrap(True)

        # Configure UPnP checkbox
        self.__upnp_checkbox.setToolTip("Allows for dynamic port-forwarding on supported routers.")

        # TODO: Add encryption key generation to this QFrame

        # Add widgets to layout
        self.__layout_manager.addWidget(port_description_label)
        self.__layout_manager.addSpacing(10)
        self.__layout_manager.addWidget(self.__upnp_checkbox)
        self.__layout_manager.addStretch()
