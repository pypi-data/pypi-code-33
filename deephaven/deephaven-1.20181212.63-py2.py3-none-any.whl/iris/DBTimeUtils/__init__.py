##########################################################################
#               This code is auto generated. DO NOT EDIT FILE!
# Run generatePythonIntegrationStaticMethods or "./gradlew :Generators:generatePythonIntegrationStaticMethods" to generate
##########################################################################

#
# Copyright (c) 2016-2018 Illumon and Patent Pending
#
import jpy
__javatype__ = None


def autoEpochToTime(epoch):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.autoEpochToTime(epoch)


def cappedTimeOffset(original,
                     period,
                     cap):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.cappedTimeOffset(original,
                                         period,
                                         cap)


def convertDateTime(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertDateTime(s)


def convertDateTimeQuiet(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertDateTimeQuiet(s)


def convertExpression(formula):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertExpression(formula)


def convertJimDateTimeQuiet(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertJimDateTimeQuiet(s)


def convertJimMicrosDateTimeQuiet(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertJimMicrosDateTimeQuiet(s)


def convertJimMicrosDateTimeQuietFast(s,
                                      timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertJimMicrosDateTimeQuietFast(s,
                                                          timeZone)


def convertJimMicrosDateTimeQuietFastTz(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertJimMicrosDateTimeQuietFastTz(s)


def convertPeriod(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertPeriod(s)


def convertPeriodQuiet(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertPeriodQuiet(s)


def convertTime(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertTime(s)


def convertTimeQuiet(s):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.convertTimeQuiet(s)


def createFormatter(timeZoneName):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.createFormatter(timeZoneName)


def currentDate(timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.currentDate(timeZone)


def currentDateNy():
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.currentDateNy()


def currentTime():
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.currentTime()


def dateAtMidnight(dateTime,
                   timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dateAtMidnight(dateTime,
                                       timeZone)


def dayDiff(start,
            end):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dayDiff(start,
                                end)


def dayOfMonth(dateTime,
               timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dayOfMonth(dateTime,
                                   timeZone)


def dayOfMonthNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dayOfMonthNy(dateTime)


def dayOfWeek(dateTime,
              timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dayOfWeek(dateTime,
                                  timeZone)


def dayOfWeekNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dayOfWeekNy(dateTime)


def dayOfYear(dateTime,
              timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dayOfYear(dateTime,
                                  timeZone)


def dayOfYearNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.dayOfYearNy(dateTime)


def diff(d1,
         d2):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.diff(d1,
                             d2)


def diffDay(start,
            end):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.diffDay(start,
                                end)


def diffNanos(d1,
              d2):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.diffNanos(d1,
                                  d2)


def diffYear(start,
             end):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.diffYear(start,
                                 end)


def expressionToNanos(formula):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.expressionToNanos(formula)


def format(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.format(*args)


def formatDate(dateTime,
               timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.formatDate(dateTime,
                                   timeZone)


def formatDateNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.formatDateNy(dateTime)


def formatNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.formatNy(dateTime)


def getExcelDateTime(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.getExcelDateTime(*args)


def getFinestDefinedUnit(timeDef):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.getFinestDefinedUnit(timeDef)


def getPartitionFromTimestampMicros(dateTimeFormatter,
                                    timestampMicros):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.getPartitionFromTimestampMicros(dateTimeFormatter,
                                                        timestampMicros)


def getPartitionFromTimestampMillis(dateTimeFormatter,
                                    timestampMillis):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.getPartitionFromTimestampMillis(dateTimeFormatter,
                                                        timestampMillis)


def getPartitionFromTimestampNanos(dateTimeFormatter,
                                   timestampNanos):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.getPartitionFromTimestampNanos(dateTimeFormatter,
                                                       timestampNanos)


def getPartitionFromTimestampSeconds(dateTimeFormatter,
                                     timestampSeconds):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.getPartitionFromTimestampSeconds(dateTimeFormatter,
                                                         timestampSeconds)


def getZonedDateTime(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.getZonedDateTime(*args)


def hourOfDay(dateTime,
              timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.hourOfDay(dateTime,
                                  timeZone)


def hourOfDayNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.hourOfDayNy(dateTime)


def isAfter(d1,
            d2):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.isAfter(d1,
                                d2)


def isBefore(d1,
             d2):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.isBefore(d1,
                                 d2)


def lastBusinessDateNy(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.lastBusinessDateNy(*args)


def lowerBin(dateTime,
             intervalNanos):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.lowerBin(dateTime,
                                 intervalNanos)


def microsOfMilli(dateTime,
                  timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.microsOfMilli(dateTime,
                                      timeZone)


def microsOfMilliNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.microsOfMilliNy(dateTime)


def microsToNanos(micros):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.microsToNanos(micros)


def microsToTime(micros):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.microsToTime(micros)


def millis(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millis(dateTime)


def millisOfDay(dateTime,
                timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisOfDay(dateTime,
                                    timeZone)


def millisOfDayNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisOfDayNy(dateTime)


def millisOfSecond(dateTime,
                   timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisOfSecond(dateTime,
                                       timeZone)


def millisOfSecondNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisOfSecondNy(dateTime)


def millisToDateAtMidnight(millis,
                           timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisToDateAtMidnight(millis,
                                               timeZone)


def millisToDateAtMidnightNy(millis):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisToDateAtMidnightNy(millis)


def millisToNanos(millis):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisToNanos(millis)


def millisToTime(millis):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.millisToTime(millis)


def minus(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.minus(*args)


def minuteOfDay(dateTime,
                timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.minuteOfDay(dateTime,
                                    timeZone)


def minuteOfDayNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.minuteOfDayNy(dateTime)


def minuteOfHour(dateTime,
                 timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.minuteOfHour(dateTime,
                                     timeZone)


def minuteOfHourNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.minuteOfHourNy(dateTime)


def monthOfYear(dateTime,
                timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.monthOfYear(dateTime,
                                    timeZone)


def monthOfYearNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.monthOfYearNy(dateTime)


def nanos(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanos(dateTime)


def nanosOfDay(dateTime,
               timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanosOfDay(dateTime,
                                   timeZone)


def nanosOfDayNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanosOfDayNy(dateTime)


def nanosOfSecond(dateTime,
                  timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanosOfSecond(dateTime,
                                      timeZone)


def nanosOfSecondNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanosOfSecondNy(dateTime)


def nanosToMicros(nanos):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanosToMicros(nanos)


def nanosToMillis(nanos):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanosToMillis(nanos)


def nanosToTime(nanos):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.nanosToTime(nanos)


def overrideLastBusinessDateNyFromCurrentDateNy():
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.overrideLastBusinessDateNyFromCurrentDateNy()


def plus(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.plus(*args)


def secondOfDay(dateTime,
                timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.secondOfDay(dateTime,
                                    timeZone)


def secondOfDayNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.secondOfDayNy(dateTime)


def secondOfMinute(dateTime,
                   timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.secondOfMinute(dateTime,
                                       timeZone)


def secondOfMinuteNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.secondOfMinuteNy(dateTime)


def secondsToNanos(seconds):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.secondsToNanos(seconds)


def secondsToTime(seconds):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.secondsToTime(seconds)


def toDateTime(zonedDateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.toDateTime(zonedDateTime)


def upperBin(*args):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.upperBin(*args)


def year(dateTime,
         timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.year(dateTime,
                             timeZone)


def yearDiff(start,
             end):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.yearDiff(start,
                                 end)


def yearNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.yearNy(dateTime)


def yearOfCentury(dateTime,
                  timeZone):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.yearOfCentury(dateTime,
                                      timeZone)


def yearOfCenturyNy(dateTime):
    global __javatype__
    if __javatype__ is None:
        __javatype__ = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
    return __javatype__.yearOfCenturyNy(dateTime)
