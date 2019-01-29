#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# slugifygui                                                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# The program is a graphical user interface to slugify text.                   #
#                                                                              #
# copyright (C) 2018 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h,--help        display help message
    --version        display version and exit
"""

name        = "slugifygui"
__version__ = "2019-01-29T1633Z"

import docopt
import logging
import os
import sys
import time

if sys.version_info[0] <= 2:
    print("Python >2 required")
    sys.exit(1)

from PyQt5.QtWidgets import (
    QApplication,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget
)
import shijian

def main():
    global options
    options = docopt.docopt(__doc__, version=__version__)
    application = QApplication(sys.argv)
    interface = Interface()
    sys.exit(application.exec_())

class Interface(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # window
        self.width_window              = 480
        self.height_window             = 665
        self.position_x_window         = 0
        self.position_y_window         = 0
        # buttons
        self.width_button              = 124
        # slugify button
        self.position_x_slugify_button = 178
        self.position_y_slugify_button = 10
        # text entry and exit boxes
        self.width_text_box            = 460
        self.height_text_box           = 300
        # text entry box
        self.position_x_text_entry     = 10
        self.position_y_text_entry     = 45
        # text exit box
        self.position_x_text_exit      = 10
        self.position_y_text_exit      = 355
        # window
        self.setWindowTitle(name)
        self.setGeometry(
            self.position_x_window,
            self.position_y_window,
            self.width_window,
            self.height_window
        )
        # button encrypt
        self.button_slugify = QPushButton("slugify", self)
        self.button_slugify.move(
            self.position_x_slugify_button,
            self.position_y_slugify_button
        )
        self.button_slugify.setFixedWidth(self.width_button)
        self.button_slugify.clicked.connect(self.slugify)
        # text entry box
        self.text_entry = QTextEdit(self)
        self.text_entry.move(
            self.position_x_text_entry,
            self.position_y_text_entry
        )
        self.text_entry.setFixedWidth(self.width_text_box)
        self.text_entry.setFixedHeight(self.height_text_box)
        # text exit box
        self.text_exit = QTextEdit(self)
        self.text_exit.move(
            self.position_x_text_exit,
            self.position_y_text_exit
        )
        self.text_exit.setFixedWidth(self.width_text_box)
        self.text_exit.setFixedHeight(self.height_text_box)
        self.show()

    def slugify(self):
        self.text_exit.setText("")
        self.text_exit.insertPlainText(shijian.slugify(
            text     = self.text_entry.toPlainText(),
            filename = True
        ))

    def closeEvent(self, event):
        sys.exit(0)

if __name__ == "__main__":
    main()
