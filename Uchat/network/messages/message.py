from datetime import datetime
from enum import Enum
from struct import Struct
import struct
from abc import abstractmethod, ABC


class MessageType(Enum):
    GREETING = 0
    CHAT = 1
    FAREWELL = 2


class Message:
    def __init__(self, m_type: MessageType):
        self.m_type: MessageType = m_type  # Type of mag

    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Abstract method that must be implemented in child classes
        Converts self to bytes to be sent over a socket

        :returns The bytes representation of self
        """
        pass


class GreetingMessage(Message, ABC):
    """
    Message used to establish communications with a peer, doubly-serving as a friend request and an introduction
    """
    _greeting_format = 'B I ? ? 20p'

    def __init__(self, color_as_int: int, username: str, ack: bool, wants_to_talk: bool = True):
        super().__init__(MessageType.GREETING)

        self.__color: int = color_as_int  # Must be encoded and decoded into 3 bytes
        self.username: str = username  # Must be between 3 - 20 characters
        self.ack: bool = ack  # True if this is acknowledging an original greeting
        self.wants_to_talk: bool = wants_to_talk  # True if the sender wants to establish communications

    def get_hex_code(self):
        return hex(self.__color)

    def to_bytes(self) -> bytes:
        return _pack(self._greeting_format, self.m_type.value, self.__color, self.ack, self.wants_to_talk,
                     self.username.encode())

    @classmethod
    def from_bytes(cls, obj_bytes: bytes):
        """
        Given a bytearray of the form { string size message_bytes }, returns a new GreetingMessage
        :param obj_bytes:
        :return:
        """
        param_tuple = Struct(GreetingMessage._greeting_format).unpack(obj_bytes)
        return cls(param_tuple[1], param_tuple[4].decode('ascii'), param_tuple[2], param_tuple[3])


class ChatMessage(Message, ABC):
    """
    Actual messages sent
    """

    def __init__(self, message: str, time_stamp=None):
        super().__init__(MessageType.CHAT)
        self.time_stamp: float = datetime.now().timestamp() if not time_stamp else time_stamp
        self.message_len: int = len(message)
        self.message = message

    def to_bytes(self) -> bytes:
        chat_format = 'B H f {}s'.format(self.message_len)
        return _pack(chat_format, self.m_type.value, self.message_len, self.time_stamp, self.message.encode())

    @classmethod
    def from_bytes(cls, obj_bytes: bytes):
        message_len = Struct('H').unpack(obj_bytes[2:4])[0]
        param_tuple = Struct('B H f {}s'.format(message_len)).unpack(obj_bytes)
        return cls(param_tuple[3].decode('ascii'), param_tuple[2])


class FarewellMessage(Message, ABC):
    _farewell_format = 'B'

    def __init__(self):
        super().__init__(MessageType.FAREWELL)

    def to_bytes(self) -> bytes:
        return _pack(FarewellMessage._farewell_format, self.m_type.value)

    @classmethod
    def from_bytes(cls):
        return cls()


def _pack(format_str: str, *packed_args) -> bytes:
    # Convert greeting msg to bytearray
    message_bytes: bytes = Struct(format_str).pack(*packed_args)
    # Insert 4 bytes of length at beginning
    return Struct('I').pack(struct.calcsize(format_str)) + message_bytes
