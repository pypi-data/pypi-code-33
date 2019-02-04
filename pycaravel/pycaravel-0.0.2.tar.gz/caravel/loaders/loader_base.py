# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module defines the loader base class.
"""

class LoaderBase(object):
    """ Base class for all loaders.
    """
    allowed_extensions = []

    def can_load(self, path):
        """ A method checking the file extension.

        Parameters
        ----------
        path: str
            the path to the data to be loaded.

        Returns
        -------
        out: bool
            True if the file extension is valid, False otherwise.
        """
        for ext in self.allowed_extensions:
            if path.endswith(ext):
                return True
        return False

    def load(self, path):
        """ A method that load the data and associated metadata.

        Parameters
        ----------
        path: str
            the path to the data to be loaded.

        Returns
        -------
        image: Data
            the loaded data.
        """
        raise NotImplementedError(
            "The 'load' method must be implemented in subclasses.")

    def can_save(self, outpath):
        """ A method checking the output file extension.

        Parameters
        ----------
        outpath: str
            the path where the the image will be saved.

        Returns
        -------
        out: bool
            True if the output file extension is valid, False otherwise.
        """
        for ext in self.allowed_extensions:
            if outpath.endswith(ext):
                return True
        return False

    def save(self, data, outpath):
        """ A method that save the data and associated metadata.

        Parameters
        ----------
        image: Data
            the data to be saved.
        outpath: str
            the path where the the data will be saved.
        """
        raise NotImplementedError(
            "The 'save' method must be implemented in subclasses.")
