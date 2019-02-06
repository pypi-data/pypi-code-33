# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/travis/build/randovania/randovania/randovania/gui/item_quantities_window.ui',
# licensing of '/home/travis/build/randovania/randovania/randovania/gui/item_quantities_window.ui' applies.
#
# Created: Wed Feb  6 04:33:05 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ItemQuantitiesWindow(object):
    def setupUi(self, ItemQuantitiesWindow):
        ItemQuantitiesWindow.setObjectName("ItemQuantitiesWindow")
        ItemQuantitiesWindow.resize(802, 488)
        self.centralWidget = QtWidgets.QWidget(ItemQuantitiesWindow)
        self.centralWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.scroll_area = QtWidgets.QScrollArea(self.centralWidget)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scroll_area.setLineWidth(0)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area_widget_contents = QtWidgets.QWidget()
        self.scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 784, 449))
        self.scroll_area_widget_contents.setObjectName("scroll_area_widget_contents")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.scroll_area_widget_contents)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.itemquantity_space_filler = QtWidgets.QLabel(self.scroll_area_widget_contents)
        self.itemquantity_space_filler.setText("")
        self.itemquantity_space_filler.setObjectName("itemquantity_space_filler")
        self.gridLayout_3.addWidget(self.itemquantity_space_filler, 2, 2, 1, 1)
        self.itemquantity_reset_button = QtWidgets.QPushButton(self.scroll_area_widget_contents)
        self.itemquantity_reset_button.setObjectName("itemquantity_reset_button")
        self.gridLayout_3.addWidget(self.itemquantity_reset_button, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 1, 0, 1, 3)
        self.itemquantity_description_label = QtWidgets.QLabel(self.scroll_area_widget_contents)
        self.itemquantity_description_label.setWordWrap(True)
        self.itemquantity_description_label.setObjectName("itemquantity_description_label")
        self.gridLayout_3.addWidget(self.itemquantity_description_label, 0, 0, 1, 3)
        self.itemquantity_total_label = QtWidgets.QLabel(self.scroll_area_widget_contents)
        self.itemquantity_total_label.setObjectName("itemquantity_total_label")
        self.gridLayout_3.addWidget(self.itemquantity_total_label, 2, 0, 1, 1)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.gridLayout.addWidget(self.scroll_area, 0, 0, 1, 2)
        ItemQuantitiesWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(ItemQuantitiesWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 802, 21))
        self.menuBar.setObjectName("menuBar")
        ItemQuantitiesWindow.setMenuBar(self.menuBar)

        self.retranslateUi(ItemQuantitiesWindow)
        QtCore.QMetaObject.connectSlotsByName(ItemQuantitiesWindow)

    def retranslateUi(self, ItemQuantitiesWindow):
        ItemQuantitiesWindow.setWindowTitle(QtWidgets.QApplication.translate("ItemQuantitiesWindow", "Someone forgot to name this", None, -1))
        self.itemquantity_reset_button.setText(QtWidgets.QApplication.translate("ItemQuantitiesWindow", "Reset", None, -1))
        self.itemquantity_description_label.setText(QtWidgets.QApplication.translate("ItemQuantitiesWindow", "<html><head/><body><p align=\"justify\">Choose how many of each item will appear in the game. Adding more than one for major upgrades makes it more likely you\'ll find that upgrade, but additional copies are useless.</p><p align=\"justify\">The total of configured items must be less than how many spots are in the game: trying to add more will fail when generating.</p><p align=\"justify\">If removing items, the remaning spots are filled with Energy Transfer Module.</p></body></html>", None, -1))
        self.itemquantity_total_label.setText(QtWidgets.QApplication.translate("ItemQuantitiesWindow", "Total Pickups: 0/0", None, -1))

