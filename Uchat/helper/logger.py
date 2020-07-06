from enum import Enum
from typing import List, Tuple
from pathlib import Path

from Uchat.helper.error import print_err


class DataType(Enum):
    LOG = 0
    USER = 1


def write_to_data_file(data_type: DataType, file_name: str, data_list: List[Tuple[str, str]]):
    try:
        file_path = Path('data')
        if data_type is DataType.LOG:
            file_path /= 'log'
            file_path /= file_name
        elif data_type is DataType.USER:
            file_path /= file_name

        with open(file_path, 'w') as f:
            for data_tuple in data_list:
                f.write('{} : {}\n'.format(data_tuple[0], data_tuple[1]))
    except OSError as err:
        print_err(1, repr(err))
