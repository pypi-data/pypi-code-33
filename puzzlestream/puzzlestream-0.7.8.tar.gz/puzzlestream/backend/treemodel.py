# -*- coding: utf-8 -*-
"""Tree model module.

contains PSTreeModel
"""

from PyQt5 import QtCore, QtGui

translate = QtCore.QCoreApplication.translate


class PSTreeModel(QtGui.QStandardItemModel):
    """Tree model class, used in data view.

    Model that displays standard keys, numpy keys, ... in different sub-trees.
    """

    def __init__(self, standardKeys, numpy2DKeys, pandasDataFrameKeys,
                 mplKeys, otherKeys, checkStates, parent=None):
        """Tree model init.

        standardKeys (list): Numpy 1D array keys.
        numpy2DKeys (list): Numpy 2D array keys.
        mplKeys (list): Matplotlib figure keys.
        otherKeys (list): Keys of all other items.
        checkStates (list): Initial states of the standard item check boxes.
        """
        self.__standardKeys = standardKeys
        self.__checkStates = checkStates
        self.__numpy2DKeys = numpy2DKeys
        self.__pandasDataFrameKeys = pandasDataFrameKeys
        self.__mplKeys = mplKeys
        self.__otherKeys = otherKeys
        super().__init__(parent)
        self.keyUpdate()

    def retranslateUi(self):
        self.__standardItem.setText(translate("TreeModel", "1D items"))
        self.__twoDItem.setText(translate("TreeModel", "2D items"))
        self.__pandasDataFrameItem.setText(
            translate("TreeModel", "Pandas data frames"))
        self.__plotItem.setText(translate("TreeModel", "Plot items"))
        self.__otherItem.setText(translate("TreeModel", "Other items"))

    def keyUpdate(self):
        """Update model from lists."""
        self.clear()
        self.__standardItem = QtGui.QStandardItem()
        self.__twoDItem = QtGui.QStandardItem()
        self.__pandasDataFrameItem = QtGui.QStandardItem()
        self.__plotItem = QtGui.QStandardItem()
        self.__otherItem = QtGui.QStandardItem()

        for key in self.__standardKeys:
            item = QtGui.QStandardItem(key)
            item.setCheckable(True)

            if key not in self.__checkStates:
                self.__checkStates[key] = True

            if self.__checkStates[key]:
                item.setCheckState(2)
            else:
                item.setCheckState(0)

            self.__standardItem.appendRow(item)

        for key in self.__numpy2DKeys:
            self.__twoDItem.appendRow(QtGui.QStandardItem(key))

        for key in self.__pandasDataFrameKeys:
            self.__pandasDataFrameItem.appendRow(QtGui.QStandardItem(key))

        for key in self.__mplKeys:
            self.__plotItem.appendRow(QtGui.QStandardItem(key))

        for key in self.__otherKeys:
            self.__otherItem.appendRow(QtGui.QStandardItem(key))

        for item in (self.__standardItem, self.__twoDItem,
                     self.__pandasDataFrameItem, self.__plotItem,
                     self.__otherItem):
            self.appendRow(item)

        self.retranslateUi()
