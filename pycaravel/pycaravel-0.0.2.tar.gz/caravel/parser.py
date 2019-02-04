# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module contains the generic parser definition.
"""

# Package import
from caravel.parsers import CWParser
from caravel.parsers import BIDSParser


# Global parameters
# > define all the available parsers
PARSERS = [CWParser, BIDSParser]


def get_parser(project, layoutdir):
    """ Method to return the appropriate parser for your study.

    Parameters
    ----------
    project: str
        the name of the project you are working on.
    layoutdir: str
        the location of the pre-generated parsing representations. If None
        switch to managers mode.

    Returns
    -------
    parser: obj
        the dataset appropriate parser.
    """
    for parser_class in PARSERS:
        parser = parser_class(project, layoutdir)
        if parser.can_load():
            return parser
    raise ValueError("No loader available for '{0}'.".format(project))




