import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class PSTablePlot(QWidget):

    def __init__(self, data):
        super().__init__()
        self.__data = data
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)
        self.setLayout(self.__layout)

        self.__curve = pg.PlotWidget()
        self.__curve.getViewBox().setBackgroundColor("w")
        self.__curve.getPlotItem().hideAxis("bottom")
        self.__curve.getPlotItem().hideAxis("left")
        self.__curve.getPlotItem().hideButtons()
        self.__curve.getPlotItem().setMenuEnabled(False)
        self.__curve.getPlotItem().setMouseEnabled(False, False)
        self.__curve.getPlotItem().plot(np.arange(len(self.__data)),
                                        self.__data,
                                        pen=pg.mkPen("k"))

        self.__hist = pg.PlotWidget()
        self.__hist.getViewBox().setBackgroundColor("w")
        self.__hist.getPlotItem().hideAxis("bottom")
        self.__hist.getPlotItem().hideAxis("left")
        self.__hist.getPlotItem().hideButtons()
        self.__hist.getPlotItem().setMenuEnabled(False)
        self.__hist.getPlotItem().setMouseEnabled(False, False)

        y, x = np.histogram(self.__data, bins=25)
        self.__hist.getPlotItem().plot(x, y, pen=pg.mkPen("r", width=3),
                                       stepMode=True)

        self.__label = QLabel()
        self.__label.setAlignment(Qt.AlignRight)

        self.__layout.addWidget(self.__curve)
        self.__layout.addWidget(self.__label)
        self.__currentPlot = self.__curve

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)

        self.setFocusPolicy(Qt.NoFocus)
        self.__curve.setFocusPolicy(Qt.NoFocus)
        self.__hist.setFocusPolicy(Qt.NoFocus)
        self.__label.setFocusPolicy(Qt.NoFocus)
        self.retranslateUi()

    def retranslateUi(self):
        if self.__currentPlot == self.__curve:
            self.__label.setText(translate("TablePlot", "curve"))

        if self.__currentPlot == self.__hist:
            self.__label.setText(translate("TablePlot", "histogram"))

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def __contextMenu(self, pos):
        menu = QMenu(self)
        curve = menu.addAction(translate("TablePlot", "curve"))
        hist = menu.addAction(translate("TablePlot", "histogram"))
        curve.triggered.connect(self.__showCurve)
        hist.triggered.connect(self.__showHist)

        if self.__currentPlot == self.__curve:
            curve.setCheckable(True)
            curve.setChecked(True)
        else:
            hist.setCheckable(True)
            hist.setChecked(True)

        return menu.exec_(self.mapToGlobal(pos))

    def __showCurve(self):
        if self.__currentPlot != self.__curve:
            self.__layout.replaceWidget(self.__currentPlot, self.__curve)
            self.__currentPlot.hide()
            self.__currentPlot = self.__curve
            self.__currentPlot.show()
            self.retranslateUi()

    def __showHist(self):
        if self.__currentPlot != self.__hist:
            self.__layout.replaceWidget(self.__currentPlot, self.__hist)
            self.__currentPlot.hide()
            self.__currentPlot = self.__hist
            self.__currentPlot.show()
            self.retranslateUi()

    def mouseDoubleClickEvent(self, event):
        if self.__currentPlot == self.__curve:
            self.__showHist()
        else:
            self.__showCurve()
        super().mouseDoubleClickEvent(event)
