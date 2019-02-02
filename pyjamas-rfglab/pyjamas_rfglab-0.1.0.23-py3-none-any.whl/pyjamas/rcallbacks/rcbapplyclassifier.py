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

import numpy
from PyQt5 import QtWidgets

import pyjamas.dialogs as dialogs
from .rcallback import RCallback


class RCBApplyClassifier(RCallback):
    def cbApplyClassifier(self, firstSlice: int = None, lastSlice: int = None) -> bool:  # Handle IO errors.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.timepoints.TimePointsDialog()
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=self.pjs.slices.shape[0])
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            firstSlice, lastSlice = ui.parameters()

            dialog.close()
        else:
            continue_flag = True

        if continue_flag:
            if firstSlice <= lastSlice:
                theslicenumbers = numpy.arange(firstSlice - 1, lastSlice, dtype=int)
            else:
                theslicenumbers = numpy.arange(lastSlice - 1, firstSlice, dtype=int)

            self.apply_classifier(theslicenumbers)

            self.pjs.repaint()

            return True
        else:
            return False

    def apply_classifier(self, theslices: numpy.ndarray) -> bool:
        self.pjs.statusbar.showMessage(f"Applying classifier to {str(len(theslices))} images. Please wait.")
        self.pjs.batch_classifier.predict(self.pjs.slices, theslices)

        # For every slice ...
        for index in theslices:
            self.add_classifier_boxes(self.pjs.batch_classifier.box_arrays[index], index)

        self.pjs.statusbar.showMessage("Done!")

        return True

    def add_classifier_boxes(self, boxes: numpy.ndarray = None, slice_index: int = None) -> bool:  # The first slice_index should be 0.
        if boxes is None or boxes is False or boxes == []:
            return False

        if slice_index is None or slice_index is False:
            slice_index = self.pjs.curslice

        for aBox in boxes:
            # Boxes stored as [minrow, mincol, maxrow, maxcol]
            self.pjs.addPolyline([[aBox[1], aBox[0]], [aBox[3], aBox[0]], [aBox[3], aBox[2]],
                                  [aBox[1], aBox[2]]], slice_index)

        return True


