from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from Uchat.MessageContext import MessageContext
from Uchat.ui.main.ProfilePhotoView import ProfilePhotoView


class MessageView(QWidget):
    """
    Used for displaying a chat message and it's associated profile photo
    """

    def __init__(self, parent: QWidget, context: MessageContext):
        super().__init__(parent)
        self.setObjectName('message-view')

        # Chat bubble
        self.__chat_bubble = QLabel(context.msg.message, self)
        self.__chat_bubble.setObjectName("chat-bubble")
        self.__chat_bubble.setWordWrap(True)
        self.__chat_bubble.setFixedHeight(self.__chat_bubble.sizeHint().height())  # Needed to prevent text clipping

        # Set time tooltip
        date = datetime.fromtimestamp(context.msg.time_stamp)
        readable_date = date.strftime('%D- %H:%M:%S')
        self.__chat_bubble.setToolTip("Sent {}".format(readable_date))

        # Profile view
        self.__sender_profile_view = ProfilePhotoView(self, context.sender.username, context.sender.color, radius=20)
        self.__layout_manager = QHBoxLayout(self)

        # Layout in proper order
        self.manage_layout(context)

    def manage_layout(self, context: MessageContext):
        """
        Organizes a message's widgets in an order reflecting conversation
        Peer's messages should be on the left side as such pfp : bubble
        Self's messages should be on the right side as such bubble: pfp
        :param context: Context of this message
        """

        pfp_flag = Qt.AlignCenter

        if context.is_sender:
            self.__layout_manager.addWidget(self.__chat_bubble)
            self.__layout_manager.addWidget(self.__sender_profile_view, 0, pfp_flag)

            background_color = 'background-color: #0080FF;'
            margin = 'margin-right: 3px;'
        else:
            self.__layout_manager.addWidget(self.__sender_profile_view, 0, pfp_flag)
            self.__layout_manager.addWidget(self.__chat_bubble)

            background_color = 'background-color: #46484b;'
            margin = 'margin-left: 3px;'

        self.__chat_bubble.setStyleSheet(self.__chat_bubble.styleSheet() + margin + background_color)
