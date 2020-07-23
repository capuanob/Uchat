from typing import List

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QAbstractScrollArea

from Uchat.MessageContext import MessageContext
from Uchat.ui.main.MessageView import MessageView


class ChatAreaView(QWidget):
    """
    Displays the messages exchanged within 1 conversation, whether it be between two or multiple peers
    """

    def __init__(self, parent: QWidget, message_contexts: List[MessageContext]):
        super().__init__(parent)
        self.setObjectName('conversation-view')

        self.contexts = list()
        self.contexts_shown = 0 # Tracks how many contexts

        self.__layout_manager = QVBoxLayout(self)

        # Scroll Area
        self.__scroll_area = QScrollArea()  # Used to scroll through messages
        for context in message_contexts:
            self.update_with(context)

        # Scroll Area Properties
        self.__scroll_area.setStyleSheet(self.__scroll_area.styleSheet() + "background-color: transparent;")
        self.__scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setWidget(self)

        self.resizeEvent = self.scroll_to_new_message

        # Set custom size hint, based off viewport size hint
        vp_size_hint_func = (lambda: QSize(self.__scroll_area.viewportSizeHint().width(),
                                           self.__scroll_area.viewportSizeHint().height() + 10))
        self.__scroll_area.sizeHint = vp_size_hint_func

    def central_widget(self):
        """
        Used for setting up conversation view from landingWindow, as the scroll area itself must be the central widget
        :return:
        """
        return self.__scroll_area

    def update_with(self, context: MessageContext):
        """
        Adds the given context's message to the scroll area
        :param context: Context of message to be added
        """
        self.contexts.append(context)
        msg = MessageView(self, context)
        self.__layout_manager.addWidget(msg, 0, context.display_flags())
        self.__scroll_area.updateGeometry()  # Updates layout on screen
        self.__scroll_area.verticalScrollBar().updateGeometry()

    def scroll_to_new_message(self, e: QResizeEvent):
        """
        Responds to an emitted resize event. Ensures a message has, indeed, been added rather than the window size
        changing size
        :return:
        """

        if len(self.contexts) != self.contexts_shown:
            # A new message has been encountered
            scroll = self.__scroll_area.verticalScrollBar()
            scroll.setValue(scroll.maximum())
            self.contexts_shown = len(self.contexts)

        QAbstractScrollArea.resizeEvent(self.__scroll_area, e)

    def displayed_messages(self):
        """
        Returns the message contexts that have been added to ChatArea
        :return:
        """

        return map(lambda x: x.msg, self.contexts)
