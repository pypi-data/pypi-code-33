##########################################################################
#               This code is auto generated. DO NOT EDIT FILE!
# Run generatePythonIntegrationStaticMethods or "./gradlew :Generators:generatePythonIntegrationStaticMethods" to generate
##########################################################################

#
# Copyright (c) 2016-2018 Illumon and Patent Pending
#
import jpy
__javatype__ = None


def calendar(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.util.calendar.Calendars")
    return __javatype__.calendar(*args)


def calendarNames():
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.util.calendar.Calendars")
    return __javatype__.calendarNames()


def getDefaultName():
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.util.calendar.Calendars")
    return __javatype__.getDefaultName()
