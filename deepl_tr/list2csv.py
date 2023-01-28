"""Convert a list to csv string and a string to list, respectively."""
import csv
import io
from typing import List, Union

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
    # convert str to [[str, ...], ...]
    data = [[elm] if isinstance(elm, str) else elm for elm in data]
    output = io.StringIO()
    try:
        writer = csv.writer(output, delimiter=",")
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

    >>> [['"cell one"'], ['cell two']] == csv2list(list2csv([['"cell one"'], ['cell two']]))
    True
    >>> [['"cell one"', 'cell two']] == csv2list(list2csv([['"cell one"', 'cell two']]))
    True
    """
    try:
        _ = [elm for elm in csv.reader(text.splitlines())]
    except Exception as exc:
        logger.error(exc)
        raise

    return _


def list2rowdata(list_: List[List[str]]) -> dict:
    """Convert a list to rowdata for ag-grid.

    The first row will be header data, conformant with csv2list(ag-grid.api.getDataAsCsv()).

    >>> _ = [['text', 'texttr'], ['', '']]
    >>> list2rowdata(_) == [{'text': '', 'texttr': ''}]
    True
    >>> list1 = [['text'], [""]]
    >>> list2rowdata(list1) == [{'text': ''}]
    True
    """
    try:
        _ = [dict(zip(list_[0], elm)) for elm in list_[1:]]
    except Exception as exc:
        logger.error(exc)
        raise

    return _
