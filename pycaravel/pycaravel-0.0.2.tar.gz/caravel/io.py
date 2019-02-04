# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module contains generic functions to load/save a dataset.
"""

# Package import
from caravel.loaders import TSV
from caravel.loaders import NIFTI

# Global parameters
# > define all the available loaders
LOADERS = [TSV, NIFTI]


def load(path, **kwargs):
    """ Load the data.

    Parameters
    ----------
    path: str
        the path to the data to be loaded.

    Returns
    -------
    data: object
        the loaded data.
    """
    loader = get_loader(path)
    return loader.load(path, **kwargs)


def save(data, path, **kwargs):
    """ Save the data.

    Parameters
    ----------
    data: object
        the data to be saved.
    path: str
        the destination file.
    """
    saver = get_saver(path)
    saver.save(data, path, **kwargs)


def get_loader(path):
    """ Search for a suitable loader in the declared loaders.
    Raise an exception if no loader is found.

    Parameters
    ----------
    path: str
        the path to the data to be loaded.

    Returns
    -------
    loader: @instance
        the loader instance.
    """
    for loader_class in LOADERS:
        loader = loader_class()
        if loader.can_load(path):
            return loader
    raise Exception("No loader available for '{0}'.".format(path))


def get_saver(path):
    """ Search for a suitable saver in the declared savers.
    Raise an exception if no saver is found.

    Parameters
    ----------
    path: str
        the path to the data to be saved.

    Returns
    -------
    saver: @instance
        the loader instance.
    """
    for saver_class in LOADERS:
        saver = saver_class()
        if saver.can_save(path):
            return saver
    raise Exception("No saver available for '{0}'.".format(path))
