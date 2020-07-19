from enum import Enum
from typing import Dict, Any
from pathlib import Path
import json

from Uchat.model.account import Account
from Uchat.helper.error import print_err


class DataType(Enum):
    LOG = 'logs'
    USER = 'user'


class FileName(Enum):
    GLOBAL = 'global.json'


def write_to_data_file(data_type: DataType, file_name: FileName, obj: Any):
    try:
        file_path = _get_file_path(data_type, file_name)
        with open(file_path, 'w') as f:
            json.dump(obj, f, default=lambda x: x.__dict__)
    except OSError as err:
        print_err(1, repr(err))


def get_user_account_data() -> Account:
    json = _get_data_from_file(DataType.USER, FileName.GLOBAL)
    return Account(**json) if json else None


def _get_data_from_file(data_type: DataType, file_name: FileName) -> Dict:
    """
    Converts a JSON file to it's respective object

    :param data_type: Represents folder to search for file in
    :param file_name: Represents file name to open in proper folderjson
    :return: Deserialized JSON object
    """

    obj = None
    try:
        file_path = _get_file_path(data_type, file_name)
        with open(file_path, 'r') as f:
            obj = json.load(f)
    except OSError as err:
        print_err(1, repr(err))

    return obj


def _get_file_path(data_type: DataType, file_name: FileName):
    """
    Forms a file path in the data folder

    :param data_type: Represents folder to search for file in
    :param file_name: Represents file name to open in proper folder
    :return: a fully formed file path (may or may not exist)
    """
    file_path = Path('data')
    file_path /= data_type.value
    file_path /= file_name.value

    return file_path
