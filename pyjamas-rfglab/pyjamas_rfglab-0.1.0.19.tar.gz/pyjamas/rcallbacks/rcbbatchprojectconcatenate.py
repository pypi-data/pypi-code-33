"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
from typing import List, Tuple

import numpy
from PyQt5 import QtWidgets

import pyjamas.dialogs as dialogs
from .rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils as rimutils
import pyjamas.rutils as rutils


class RCBBatchProjectConcat(RCallback):
    DEFAULT_FILE_NAME: str = 'projected'
    VALID_EXTENSIONS: Tuple[str] = ('.tif', '.tiff')
    OUTPUT_EXTENSION: str = '.tif'

    def cbBatchProjectConcat(self, input_folder_name: str = None, slice_str: str = None, output_file_name: str = None) \
            -> bool:
        # If not enough parameters, open dialog.
        if input_folder_name == '' or input_folder_name is False or not os.path.exists(
                input_folder_name):  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            dialog = QtWidgets.QDialog()
            ui = dialogs.batchprojectconcat.BatchProjectConcatenateDialog()
            ui.setupUi(dialog)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with supplied parameters
        else:
            theparameters = {'input_folder': input_folder_name,
                             'slice_list': slice_str,
                             'file_name': output_file_name}
            continue_flag = True

        if continue_flag:
            return_value = self.batch_project_concatenate(theparameters)

            if return_value:
                self.pjs.cwd = os.path.abspath(theparameters['input_folder'])

            return return_value
        else:
            return False

    def batch_project_concatenate(self, parameters: dict = None) -> bool:
        folder_name: str = parameters.get('input_folder', None)
        slices: str = parameters.get('slice_list', None)
        file_name: str = parameters.get('file_name', None)
        if file_name[-4:] != RCBBatchProjectConcat.OUTPUT_EXTENSION:
            file_name = file_name + RCBBatchProjectConcat.OUTPUT_EXTENSION

        assert os.path.exists(folder_name), 'Output folder does not exist!'

        file_list: List[str] = os.listdir(folder_name)
        file_list.sort(key=rutils.RUtils.natural_sort)

        n_files: int = len(file_list)

        projected_image: numpy.ndarray = None
        projected_array: numpy.ndarray = None

        self.pjs.statusbar.showMessage(f"Processing stacks in {folder_name} ...")

        for ind, thefile in enumerate(file_list):
            self.pjs.statusbar.showMessage(f"Processing file {ind+1} / {n_files} ...")

            _, extension = os.path.splitext(thefile)

            if extension.lower() in RCBBatchProjectConcat.VALID_EXTENSIONS:
                theimage: numpy.ndarray = rimutils.read_stack(os.path.join(folder_name, thefile))

                if slices == '' or not slices:
                    projected_image = numpy.expand_dims(rimutils.mip(theimage), axis=0)
                else:
                    slice_list: List[int] = rutils.RUtils.parse_range_list(slices)
                    projected_image = numpy.expand_dims(rimutils.mip(theimage[slice_list]), axis=0)

                if projected_array is not None:
                    projected_array = numpy.concatenate((projected_array, projected_image), axis=0)

                else:
                    projected_array = projected_image.copy()

        self.pjs.statusbar.showMessage("Done!")

        # Now write the file.
        rimutils.write_stack(os.path.join(folder_name, file_name), projected_array)

        return True
