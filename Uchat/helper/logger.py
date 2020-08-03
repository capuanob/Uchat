"""
Handles logging of pertinent data for session persistence
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import pickle
import os.path

from Uchat.model.account import Account
from Uchat.helper.error import print_err
from Uchat.peer import Peer


class DataType(Enum):
    """
    Enumerates types of data that can be logged (used for determining folder)
    """
    LOG = 'logs'
    USER = 'user'


class FileName(Enum):
    """
    Enumerates file names for logging
    """
    GLOBAL = 'global.json'
    FRIENDS = 'friends.json'


def write_to_data_file(data_type: DataType, file_name: FileName, obj: Any, append_mode: bool):
    """
    Saves an object as json
    :param data_type: Folder to save to
    :param file_name: File to save to
    :param obj: Object to be serialized as json
    :param append_mode: Whether or not the data should be appended or overwrite existing content
    """

    try:
        file_path = _get_file_path(data_type, file_name)
        with open(file_path, 'ab' if append_mode else 'wb') as file:
            pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)
    except OSError as err:
        print_err(1, repr(err))


def get_user_account_data() -> Optional[Account]:
    """
    Deserialized user's account data
    :return: an Account object containing the user's account details
    """

    json_data = _get_data_from_file(DataType.USER, FileName.GLOBAL)
    return json_data


def get_friends() -> List[Peer]:
    """
    Converts a JSON file to it's respective list of objects
    :return:
    """

    friends = list()

    if json_list := _get_data_list_from_file(DataType.USER, FileName.FRIENDS):
        for friend in json_list:
            friends.append(friend)

    return friends


def _get_data_from_file(data_type: DataType, file_name: FileName) -> Dict:
    """
    Converts a JSON file to it's respective object

    :param data_type: Represents folder to search for file in
    :param file_name: Represents file name to open in proper folderjson
    :return: Deserialized JSON object
    """

    obj = None
    file_path = _get_file_path(data_type, file_name)

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            obj = pickle.load(file)
    return obj


def _get_data_list_from_file(data_type: DataType, file_name: FileName) -> List:
    """
    Converts a JSON file ot it's respective list of objects

    :param data_type: Represents folder to search for file in
    :param file_name: Represents file name to open in proper folderjson
    :return: Deserialized JSON object(s)
    """
    objs = []
    file_path = _get_file_path(data_type, file_name)

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            while 1:
                try:
                    objs.append(pickle.load(file))
                except EOFError:
                    break
    return objs


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
