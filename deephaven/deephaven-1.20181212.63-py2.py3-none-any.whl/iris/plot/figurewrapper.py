####################################################################################
#               This code is auto generated. DO NOT EDIT FILE!
# Run generatePythonFigureWrapper or "./gradlew :Generators:generatePythonFigureWrapper" to generate
####################################################################################

#
# Copyright (c) 2016-2018 Illumon and Patent Pending
#
import jpy
import sys
import time


def __iswidget__(obj):
    if obj is None:
        return False
    return type(obj).__name__ == 'FigureWidget'

def __create_java_array__(obj):
    if isinstance(obj, list):
        type_ = __get_type__(obj)
        return jpy.array(type_, obj) if type_ != "com.illumon.iris.db.tables.utils.DBDateTime" else __encode_datetime64__(obj)
    elif isinstance(obj, str):
        return obj

    try:
        l = list(obj)
        return __create_java_array__(l)
    except TypeError:
        return obj

def __get_type__(list):
    if len(list) > 0:
        type_ = type(list[0]).__name__
        if type_ == 'datetime':
            return 'com.illumon.iris.db.tables.utils.DBDateTime'
        if type_ == 'str':
            return 'java.lang.String'
        if type_ == 'int':
            return 'long'
        return type_

def __encode_datetime64__(list):
    DBDateTime = jpy.__get_type__('com.illumon.iris.db.tables.utils.DBDateTime')
    a = jpy.array("com.illumon.iris.db.tables.utils.DBDateTime", len(list))

    if sys.version_info[0] > 2:
        cst = int
    else:
        cst = long

    for i in range(len(list)):
        v = list[i]
        if v == None:
            a[i] = None
        else:
            ns = cst(time.mktime(v.timetuple()))*1000000000 + v.microsecond*1000
            t = DBDateTime(ns)
            a[i] = t

    return a

def __create_string_array__(list):
    numel = len(list)
    stringarray = jpy.array('java.lang.String', numel)
    String = jpy.__get_type__('java.lang.String')
    for i in Range(0, numel):
        stringarray[i] = String(list[i])
        return stringarray

class FigureWrapper:
    def __init__(self, figure, *args):
        plotting_convenience = jpy.get_type("com.illumon.iris.db.plot.PlottingConvenience")
        numargs = len(args)
        if figure is None:
            if numargs == 0:
                self.figure_ = plotting_convenience.figure()
            elif numargs == 2:
                self.figure_ = plotting_convenience.figure(args[0], args[1])
            else:
                raise ValueError("Number of arguments to create a Figure must be 0 or 2: was %d"%numargs)
        else:
            self.figure_ = figure

        self.valid_groups = None

    def show(self):
            FigureWidget = jpy.get_type('com.illumon.iris.db.plot.FigureWidget')
            figure = FigureWidget(self.figure_)
            return FigureWrapper(figure)

    def getwidget(self):
        if __iswidget__(self.figure_):
            return self.figure_
        return None

    def get_valid_groups(self):
        return __create_java_array__(self.valid_groups)

    def setValidGroups(self, groups):
        self.valid_groups = groups

    def axes(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.axes(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def axesRemoveSeries(self, *args):
        __numargs = len(args)
        if __numargs >= 0:
            figure = self.figure_.axesRemoveSeries(__create_java_array__(args[0:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def axis(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.axis(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def axisColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.axisColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def axisFormat(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.axisFormat(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def axisFormatPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.axisFormatPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def axisLabel(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.axisLabel(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def axisLabelFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.axisLabelFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.axisLabelFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def businessTime(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.businessTime()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.businessTime(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def catErrorBar(self, *args):
        __numargs = len(args)
        if __numargs == 5:
            figure = self.figure_.catErrorBar(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        if __numargs == 6:
            figure = self.figure_.catErrorBar(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def catErrorBarBy(self, *args):
        __numargs = len(args)
        if __numargs >= 6:
            figure = self.figure_.catErrorBarBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def catHistPlot(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.catHistPlot(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.catHistPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def catPlot(self, *args):
        __numargs = len(args)
        if __numargs == 3:
            figure = self.figure_.catPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.catPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def catPlot3d(self, *args):
        __numargs = len(args)
        if __numargs == 4:
            figure = self.figure_.catPlot3d(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs == 5:
            figure = self.figure_.catPlot3d(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def catPlot3dBy(self, *args):
        __numargs = len(args)
        if __numargs >= 5:
            figure = self.figure_.catPlot3dBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def catPlotBy(self, *args):
        __numargs = len(args)
        if __numargs >= 4:
            figure = self.figure_.catPlotBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def chart(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.chart(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.chart(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def chartRemoveSeries(self, *args):
        __numargs = len(args)
        if __numargs >= 0:
            figure = self.figure_.chartRemoveSeries(__create_java_array__(args[0:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def chartTitle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.chartTitle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def chartTitleColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.chartTitleColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def chartTitleFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.chartTitleFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.chartTitleFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def colSpan(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.colSpan(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def errorBarX(self, *args):
        __numargs = len(args)
        if __numargs == 5:
            figure = self.figure_.errorBarX(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        if __numargs == 6:
            figure = self.figure_.errorBarX(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def errorBarXBy(self, *args):
        __numargs = len(args)
        if __numargs >= 6:
            figure = self.figure_.errorBarXBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def errorBarXY(self, *args):
        __numargs = len(args)
        if __numargs == 7:
            figure = self.figure_.errorBarXY(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6]))
            return FigureWrapper(figure)
        if __numargs == 8:
            figure = self.figure_.errorBarXY(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6]), __create_java_array__(args[7]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def errorBarXYBy(self, *args):
        __numargs = len(args)
        if __numargs >= 8:
            figure = self.figure_.errorBarXYBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6]), __create_java_array__(args[7]), __create_java_array__(args[8:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def errorBarY(self, *args):
        __numargs = len(args)
        if __numargs == 5:
            figure = self.figure_.errorBarY(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        if __numargs == 6:
            figure = self.figure_.errorBarY(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def errorBarYBy(self, *args):
        __numargs = len(args)
        if __numargs >= 6:
            figure = self.figure_.errorBarYBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def figureRemoveSeries(self, *args):
        __numargs = len(args)
        if __numargs >= 0:
            figure = self.figure_.figureRemoveSeries(__create_java_array__(args[0:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def figureTitle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.figureTitle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def figureTitleColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.figureTitleColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def figureTitleFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.figureTitleFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.figureTitleFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def funcNPoints(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.funcNPoints(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def funcRange(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.funcRange(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.funcRange(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.funcRange(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs == 5:
            figure = self.figure_.funcRange(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def gradientVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.gradientVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.gradientVisible(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def group(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.group(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.group(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def histPlot(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.histPlot(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.histPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.histPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs == 5:
            figure = self.figure_.histPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        if __numargs == 6:
            figure = self.figure_.histPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def invert(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.invert()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.invert(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def legendColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.legendColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def legendFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.legendFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.legendFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def legendVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.legendVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def lineColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.lineColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.lineColor(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def lineStyle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.lineStyle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.lineStyle(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def linesVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.linesVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.linesVisible(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def log(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.log()
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def max(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.max(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def min(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.min(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def minorTicks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.minorTicks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def minorTicksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.minorTicksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def newAxes(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.newAxes()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.newAxes(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.newAxes(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def newChart(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.newChart()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.newChart(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.newChart(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def ohlcPlot(self, *args):
        __numargs = len(args)
        if __numargs == 6:
            figure = self.figure_.ohlcPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]))
            return FigureWrapper(figure)
        if __numargs == 7:
            figure = self.figure_.ohlcPlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def ohlcPlotBy(self, *args):
        __numargs = len(args)
        if __numargs >= 7:
            figure = self.figure_.ohlcPlotBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5]), __create_java_array__(args[6]), __create_java_array__(args[7:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def piePlot(self, *args):
        __numargs = len(args)
        if __numargs == 3:
            figure = self.figure_.piePlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.piePlot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def plot(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.plot(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.plot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.plot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs == 5:
            figure = self.figure_.plot(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def plot3d(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.plot3d(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.plot3d(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs == 5:
            figure = self.figure_.plot3d(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def plot3dBy(self, *args):
        __numargs = len(args)
        if __numargs >= 5:
            figure = self.figure_.plot3dBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4]), __create_java_array__(args[5:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def plotBy(self, *args):
        __numargs = len(args)
        if __numargs >= 4:
            figure = self.figure_.plotBy(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]), __create_java_array__(args[4:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def plotOrientation(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.plotOrientation(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def plotStyle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.plotStyle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def pointColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.pointColor(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.pointColor(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.pointColor(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs >= 0:
            figure = self.figure_.pointColor(__create_java_array__(args[0:]))
            return FigureWrapper(figure)

    def pointColorByY(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointColorByY(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.pointColorByY(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def pointColorInteger(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointColorInteger(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.pointColorInteger(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def pointLabel(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointLabel(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.pointLabel(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.pointLabel(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.pointLabel(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs >= 0:
            figure = self.figure_.pointLabel(__create_java_array__(args[0:]))
            return FigureWrapper(figure)

    def pointLabelFormat(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointLabelFormat(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.pointLabelFormat(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def pointShape(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointShape(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.pointShape(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.pointShape(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs >= 0:
            figure = self.figure_.pointShape(__create_java_array__(args[0:]))
            return FigureWrapper(figure)

    def pointSize(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointSize(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.pointSize(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.pointSize(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        if __numargs == 4:
            figure = self.figure_.pointSize(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]), __create_java_array__(args[3]))
            return FigureWrapper(figure)
        if __numargs >= 0:
            figure = self.figure_.pointSize(__create_java_array__(args[0:]))
            return FigureWrapper(figure)

    def pointsVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.pointsVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.pointsVisible(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def range(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.range(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def removeChart(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.removeChart(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.removeChart(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def rowSpan(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.rowSpan(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def save(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.save(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.save(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def series(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.series(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def seriesColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.seriesColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.seriesColor(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def seriesNamingFunction(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.seriesNamingFunction(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def span(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.span(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def theme(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.theme(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def tickLabelAngle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.tickLabelAngle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def ticks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.ticks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def ticksFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.ticksFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.ticksFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def ticksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.ticksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def toolTipPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.toolTipPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.toolTipPattern(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def transform(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.transform(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def twin(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.twin()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.twin(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 2:
            figure = self.figure_.twin(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def twinX(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.twinX()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.twinX(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def twinY(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.twinY()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.twinY(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def twinZ(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.twinZ()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.twinZ(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def updateInterval(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.updateInterval(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xAxis(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.xAxis()
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xBusinessTime(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.xBusinessTime()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.xBusinessTime(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xFormat(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xFormat(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xFormatPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xFormatPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xInvert(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.xInvert()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.xInvert(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xLabel(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xLabel(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xLabelFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xLabelFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.xLabelFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xLog(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.xLog()
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xMax(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xMax(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xMin(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xMin(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xMinorTicks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xMinorTicks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xMinorTicksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xMinorTicksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xRange(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.xRange(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xTickLabelAngle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xTickLabelAngle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xTicks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xTicks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xTicksFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xTicksFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.xTicksFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xTicksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xTicksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xToolTipPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xToolTipPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.xToolTipPattern(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def xTransform(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.xTransform(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yAxis(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.yAxis()
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yBusinessTime(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.yBusinessTime()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.yBusinessTime(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yFormat(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yFormat(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yFormatPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yFormatPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yInvert(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.yInvert()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.yInvert(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yLabel(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yLabel(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yLabelFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yLabelFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.yLabelFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yLog(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.yLog()
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yMax(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yMax(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yMin(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yMin(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yMinorTicks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yMinorTicks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yMinorTicksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yMinorTicksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yRange(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.yRange(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yTickLabelAngle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yTickLabelAngle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yTicks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yTicks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yTicksFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yTicksFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.yTicksFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yTicksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yTicksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yToolTipPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yToolTipPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs >= 1:
            figure = self.figure_.yToolTipPattern(__create_java_array__(args[0]), __create_java_array__(args[1:]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def yTransform(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.yTransform(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zAxis(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.zAxis()
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zBusinessTime(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.zBusinessTime()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.zBusinessTime(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zColor(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zColor(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zFormat(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zFormat(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zFormatPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zFormatPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zInvert(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.zInvert()
            return FigureWrapper(figure)
        if __numargs == 1:
            figure = self.figure_.zInvert(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zLabel(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zLabel(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zLabelFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zLabelFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.zLabelFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zLog(self, *args):
        __numargs = len(args)
        if __numargs == 0:
            figure = self.figure_.zLog()
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zMax(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zMax(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zMin(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zMin(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zMinorTicks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zMinorTicks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zMinorTicksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zMinorTicksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zRange(self, *args):
        __numargs = len(args)
        if __numargs == 2:
            figure = self.figure_.zRange(__create_java_array__(args[0]), __create_java_array__(args[1]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zTickLabelAngle(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zTickLabelAngle(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zTicks(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zTicks(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zTicksFont(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zTicksFont(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        if __numargs == 3:
            figure = self.figure_.zTicksFont(__create_java_array__(args[0]), __create_java_array__(args[1]), __create_java_array__(args[2]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zTicksVisible(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zTicksVisible(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zToolTipPattern(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zToolTipPattern(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

    def zTransform(self, *args):
        __numargs = len(args)
        if __numargs == 1:
            figure = self.figure_.zTransform(__create_java_array__(args[0]))
            return FigureWrapper(figure)
        raise NameError('No java method matches the number of input arguments')

