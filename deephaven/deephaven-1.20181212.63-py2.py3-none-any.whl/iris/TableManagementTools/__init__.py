##########################################################################
#               This code is auto generated. DO NOT EDIT FILE!
# Run generatePythonIntegrationStaticMethods or "./gradlew :Generators:generatePythonIntegrationStaticMethods" to generate
##########################################################################

#
# Copyright (c) 2016-2018 Illumon and Patent Pending
#
import jpy
__javatype__ = None


def addColumns(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.addColumns(*args)


def addGroupingMetadata(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.addGroupingMetadata(*args)


def appendToTable(tableToAppend,
                  destDir):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.appendToTable(tableToAppend,
                                      destDir)


def appendToTables(definitionToAppend,
                   tablesToAppend,
                   destinationDirectoryNames):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.appendToTables(definitionToAppend,
                                       tablesToAppend,
                                       destinationDirectoryNames)


def deleteTable(path):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.deleteTable(path)


def dropColumns(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.dropColumns(*args)


def flushColumnData():
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.flushColumnData()


def getAllDbDirs(tableName,
                 rootDir,
                 levelsDepth):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.getAllDbDirs(tableName,
                                     rootDir,
                                     levelsDepth)


def readTable(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.readTable(*args)


def renameColumns(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.renameColumns(*args)


def updateColumns(currentDefinition,
                  rootDir,
                  levels,
                  *updates):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.updateColumns(currentDefinition,
                                      rootDir,
                                      levels,
                                      *updates)


def writeColumn(sourceTable,
                destinationTable,
                pendingCount,
                columnDefinition,
                currentMapping,
                currentSize):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.writeColumn(sourceTable,
                                    destinationTable,
                                    pendingCount,
                                    columnDefinition,
                                    currentMapping,
                                    currentSize)


def writeTable(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.writeTable(*args)


def writeTables(sources,
                tableDefinition,
                destinations):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
    return __javatype__.writeTables(sources,
                                    tableDefinition,
                                    destinations)
