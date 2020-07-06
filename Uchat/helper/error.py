from enum import Enum
from sys import stderr
from typing import Dict

error_codes: Dict[int, str] = {
    1: 'FILE I/O error',
    99: 'Unknown error occurred'
}


def print_err(error_code: int, additional_info: str = ''):
    """
    Logs an encounted error, its error code, and any additional information

    :param error_code: Error code of error encountered, used for troubleshooting
    :param additional_info: Optional string containing additional information about the error
    """
    if error_code not in error_codes:
        error_code = 99  # Unknown error code

    print('{} : {}'.format(error_code, error_codes[error_code]), file=stderr)
    if additional_info:
        print("Additional information\n\n{}".format(additional_info))

