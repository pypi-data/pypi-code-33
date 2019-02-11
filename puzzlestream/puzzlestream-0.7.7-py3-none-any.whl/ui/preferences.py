# -*- coding: utf-8 -*-
"""Preferences window module.

contains PSPreferencesWindow, a subclass of QMainWindow
"""

import os

from puzzlestream.ui.translate import changeLanguage
from PyQt5 import QtCore, QtWidgets

translate = QtCore.QCoreApplication.translate


class PSPreferencesWindow(QtWidgets.QMainWindow):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setGeometry(200, 200, 480, 240)
        self.tab = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab)
        self.__config = config

        self.generalTab = QtWidgets.QWidget()
        self.generalTabLayout = QtWidgets.QGridLayout(self.generalTab)
        self.tab.addTab(self.generalTab, "General")

        self.appearanceTab = QtWidgets.QWidget()
        self.appearanceTabLayout = QtWidgets.QGridLayout(self.appearanceTab)
        self.tab.addTab(self.appearanceTab, "Appearance")

        self.__generalKeys = ["language", "autoformatOnSave", "saveOnRun",
                              "saveOnEditorFocusOut", "numberOfProcesses"]
        self.__appearanceKeys = ["design", "clockOnlyFullscreen",
                                 "slowerRedraw"]

        self.__labels = {}

        for i, key in enumerate(self.__generalKeys):
            self.addSetting(key, self.generalTabLayout, i)

        for i, key in enumerate(self.__appearanceKeys):
            self.addSetting(key, self.appearanceTabLayout, i)

        self.retranslateUi()

    def retranslateUi(self):
        self.tab.setTabText(0, translate("Preferences", "General"))
        self.tab.setTabText(1, translate("Preferences", "Appearance"))

        for key in self.__labels:
            if key in self.__config.translations:
                self.__labels[key].setText(
                    translate("Preferences", self.__config.translations[key]))

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def addSetting(self, key, tabLayout, row):
        label = QtWidgets.QLabel()
        label.setText(key)
        self.__labels[key] = label
        tabLayout.addWidget(label, row, 0)

        value = self.__config[key]

        if isinstance(value, bool):
            item = QtWidgets.QCheckBox()
            item.setChecked(value)
            item.stateChanged.connect(
                lambda info, key=key: self.__edit(key, info))

        elif (isinstance(value, str) or isinstance(value, int) or
                isinstance(value, float)):
            item = QtWidgets.QLineEdit()
            item.setText(str(value))
            item.returnPressed.connect(
                lambda info=item, key=key: self.__edit(key, info))

        elif isinstance(value, list):
            item = QtWidgets.QComboBox()
            for i in value[1]:
                item.addItem(translate("Preferences", i))
            item.setEditable(False)
            item.setCurrentIndex(value[0])
            item.currentIndexChanged.connect(
                lambda info, key=key: self.__edit(key, info)
            )

        tabLayout.addWidget(item, row, 1)

    def __edit(self, key, info):
        if isinstance(self.__config[key], bool):
            self.__config[key] = info == 2
        elif isinstance(self.__config[key], str):
            self.__config[key] = info.displayText()
        elif isinstance(self.__config[key], int):
            try:
                self.__config[key] = int(info.displayText())
            except Exception:
                pass
        elif isinstance(self.__config[key], float):
            try:
                self.__config[key] = float(info.displayText())
            except Exception:
                pass
        elif isinstance(self.__config[key], list):
            value = self.__config[key]
            value[0] = info
            self.__config[key] = value

        self.__react(key, info)

    def __react(self, key, info):
        if key == "language":
            value = self.__config[key]
            language = value[1][value[0]]

            if info == 1:
                changeLanguage(language)
            else:
                changeLanguage()
