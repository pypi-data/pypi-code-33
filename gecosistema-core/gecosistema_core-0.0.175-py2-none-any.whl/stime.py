# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        stime.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     08/08/2018
# -------------------------------------------------------------------------------
from .strings import isstring
import datetime

def now():
    """
    now - shortcut for datetime.datetime.now
    """
    return datetime.datetime.now()

def tomorrow(date=None, days=1):
    """
    tomorrow
    """
    date = ctod(date) if date else datetime.datetime.now()
    return date + datetime.timedelta(days=days)

def drange(bdate, edate):
    """
    drange - array of dates from badate to edate (included)
    """
    bdate,edate = ctod(bdate),ctod(edate)
    n = int((edate-bdate).days)
    return [ tomorrow(bdate,j) for j in range(0,n) ]

def time_from(t):
    """
    time_from -  return the time (seconds) from time t
    """
    return (datetime.datetime.now()-t).total_seconds()

def checkpoint(t, name = ""):
    """
    checkpoint
    """
    print("Time elapsed from %s: %ss."%(name,time_from(t)))

def ctod(text):
    """
    ctod - parse text to date/ datime
    """
    if isinstance(text, (datetime.datetime, datetime.date,)):
        return text

    text = text.replace("-","").replace(":","").replace(".","").replace(" ","")

    if len(text)==8:
        return datetime.datetime.strptime(text,"%Y%m%d").date()
    elif len(text)==10:
        return datetime.datetime.strptime(text, "%Y%m%d%H")
    elif len(text)==12:
        return datetime.datetime.strptime(text, "%Y%m%d%H%M")
    elif len(text)==14:
        return datetime.datetime.strptime(text, "%Y%m%d%H%M%S")
    return None

def strftime(frmt, text):
    """
    strftime
    """
    if not text:
        return datetime.datetime.now()
    elif isinstance(text, (datetime.datetime,datetime.date,) ):
        return text.strftime(frmt)
    elif isstring(text):
        date = datetime.datetime.strptime(text, "%Y-%m-%d")
        return date.strftime(frmt)

    return ""

def today():
    """
    today
    """
    d = datetime.datetime.today()
    return datetime.date(d.year,d.month,d.day)

def yesterday(Date=None,N=1):
    """
    yesterday
    """
    Date = ctod() if not Date else ctod(Date)
    return Date - datetime.timedelta(days=N)

def tomorrow(Date=None,N=1):
    """
    tomorrow
    """
    Date = ctod() if not Date else ctod(Date)
    return Date + datetime.timedelta(days=N)

def month_diff(dateA,dateB):
    """
    month_diff - Month difference
    """
    periodA = strftime("%Y%m",dateA)
    YA, mA = int(periodA[:4]), int(periodA[4:])
    periodB = strftime("%Y%m",dateB)
    YB, mB = int(periodB[:4]), int(periodB[4:])
    return (YA-YB)*12 + (mA-mB)

def firstdayofmonth(date):
    """
    firstdayofmonth
    """
    if isstring(date) and len(date)==6:
        date = datetime.datetime.strptime(date+"01","%Y%m%d").date()
    elif isstring(date) and len(date)==10 and "-" in date:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    date = strftime("%Y-%m-01", date)
    return datetime.datetime.strptime(date,"%Y-%m-%d").date()

def lastdayofmonth(date):
    """
    lastdayofmonth
    """
    date = firstdayofmonth(date)

    for d in (28, 29, 30, 31):
        date1 = datetime.date(date.year, date.month, d)
        if (date1 + datetime.timedelta(days=1)).month != date.month:
            return date1
    return None

def days_of_month(date):
    """
    days_of_month
    """
    return int(strftime("%d", lastdayofmonth(date)))

def next_period(date, n=1):
    """
    next_period
    """
    date = firstdayofmonth(date)
    for j in range(n):
        date += datetime.timedelta(days=days_of_month(date))
    return strftime("%Y%m",date)

def season(date):
    """
    season
    """
    mmdd = strftime("%m-%d", date)
    if mmdd >= "03-21" and  mmdd < "06-21":
        return "spring"
    elif mmdd >= "06-21" and  mmdd < "09-23":
        return "summer"
    elif mmdd >= "09-23" and mmdd < "12-21":
        return "autumn"
    else:
        return "winter"
