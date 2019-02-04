# coding: utf-8
##########################################################################
# NSAp - Copyright (C) CEA, 2019
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
This module defines the NIFTI dataset loader.
"""

# Third party import
import nibabel

# Package import
from .loader_base import LoaderBase


class NIFTI(LoaderBase):
    """ Define the Nifti loader.
    """
    allowed_extensions = [".nii", ".nii.gz"]

    def load(self, path):
        """ A method that load the image.

        Parameters
        ----------
        path: str
            the path to the image to be loaded.

        Returns
        -------
        data: nibabel Nifti1Image
            the loaded image.
        """
        return nibabel.load(path)

    def save(self, data, outpath):
        """ A method that save the image.

        Parameters
        ----------
        data: nibabel Nifti1Image
            the image to be saved.
        outpath: str
            the path where the the image will be saved.
        """
        nibabel.save(data, outpath)
