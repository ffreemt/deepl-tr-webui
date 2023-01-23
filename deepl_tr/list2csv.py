"""Convert a list to csv string and a string to list, respectively."""
from typing import List, Union
import io
import csv
from loguru import logger


def list2csv(data: List[Union[str, List[str]]]) -> str:
    """Convert a list to csv string.

    Args:
        data: list of cells or list of list of cells

    Returns:
        a string
    >>> list2csv(['"cell one"', 'cell two']).splitlines().__len__() == 2
    True
    >>> data = [['"cell one"', 'cell two'], ['cell three', 'cell four']]
    >>> list2csv(data).splitlines().__len__() == 2
    True
    """
    # convert str to [str]
    data = [[elm] if isinstance(elm, str) else elm for elm in data]
    output = io.StringIO()
    try:
        writer = csv.writer(output, delimiter=',')
        writer.writerows(data)
    except Exception as exc:
        logger.error(exc)
        raise

    return output.getvalue()


def csv2list(text: str) -> List[List[str]]:
    """Reverse list2csv.

    Args:
        text: csv data

    Returns:
        list of list of string
    """
    try:
        _ = [[elm] for elm in csv.reader(text.splitlines())]
    except Exception as exc:
        logger.error(exc)
        raise

    return _
