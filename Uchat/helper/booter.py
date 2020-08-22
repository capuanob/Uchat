"""
Methods that must be executed in the application's boot sequence
"""
from typing import Optional

from PyQt5.QtCore import QThread, QObject, pyqtSignal

from Uchat.helper.globals import LISTENING_PORT
from Uchat.helper.logger import get_user_account_data
from Uchat.model.account import Account
from Uchat.network.upnp import ensure_port_is_forwarded, delete_port_mapping


class BootThread(QThread):
    # SIGNALS
    """
    int: error code
    str: error msg
    """
    upnp_exception_raised = pyqtSignal(int, str)

    def __init__(self, parent: QObject, account: Optional[Account]):
        super().__init__(parent)
        self.__user_account = account

    def execute_main_prereqs(self):
        """
        Execute prerequisites for full-functionality of the main conversation view
        :return:
        """

        # PORT FORWARDING
        if self.__user_account and self.__user_account.upnp():
            # Account exists and UPnP was approved
            try:
                ensure_port_is_forwarded()
            except Exception:
                self.upnp_exception_raised.emit(4, "Unable to set up UPnP port mapping. Please enable UPnP on your "
                                                   "router or statically port-forward {} to receive conversation "
                                                   "requests.".format(LISTENING_PORT))

    def account(self, new_account: Optional[Account] = None) -> Optional[Account]:
        if new_account:
            self.__user_account = new_account
        return self.__user_account

    # Override
    def run(self):
        self.execute_main_prereqs()
        self.finished.emit()


def execute_closure_methods():
    """
    Executes prerequisites for a successful closing of the program
    """
    user_account = get_user_account_data()
    # PORT FORWARDING
    if user_account and user_account.upnp():
        # Account exists and UPnP was approved
        delete_port_mapping()
