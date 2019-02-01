# -*- coding: utf-8 -*-


def to_text(path):
    """Read text from given file.

    Parameters
    ----------
    path : str
        path of electronic invoice in JPG or PNG format

    Returns
    -------
    extracted_str : str
        returns extracted text any out file

    """
    file = open(path, "r")
    return file.read()
