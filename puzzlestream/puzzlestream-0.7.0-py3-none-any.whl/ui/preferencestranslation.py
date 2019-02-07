# -*- coding: utf-8 -*-
"""Preferences translation module.

This module is a helper file for the translation of the Puzzlestream settings.
"""

from PyQt5.QtCore import *

translate = QCoreApplication.translate

translate("Preferences", "Number of concurrent processes\n(0 = " +
          "number of CPU cores, recommended)")
translate("Preferences", "Language")
translate("Preferences", "Show clock only when in full screen")
translate("Preferences", "Save before running modules")
translate("Preferences", "Save when editor loses focus")
translate("Preferences",
          "Slower drawing (activate if the\npuzzle view is not " +
          "redrawn correctly)")
translate("Preferences", "Design")
translate("Preferences", "dark")
translate("Preferences", "light")
