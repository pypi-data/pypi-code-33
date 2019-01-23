##########################################################################
#               This code is auto generated. DO NOT EDIT FILE!
# Run generatePythonIntegrationStaticMethods or "./gradlew :Generators:generatePythonIntegrationStaticMethods" to generate
##########################################################################

#
# Copyright (c) 2016-2018 Illumon and Patent Pending
#
import jpy
__javatype__ = None


def addObjectFields(object):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.select.QueryScope")
    return __javatype__.addObjectFields(object)


def addParam(name,
             value):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.select.QueryScope")
    return __javatype__.addParam(name,
                                 value)


def getDefaultInstance():
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.select.QueryScope")
    return __javatype__.getDefaultInstance()


def getParamValue(name):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.select.QueryScope")
    return __javatype__.getParamValue(name)


def setDefaultInstance(queryScope):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.select.QueryScope")
    return __javatype__.setDefaultInstance(queryScope)
