# -*- coding: utf-8 -*-
"""
This is a submodule of fk_lib.
The moudle contains several functions and a class to calculate time.
"""
import datetime
import time
import re
class FKLTimeInfo:
    """
    This class contains all the time information, including year, month, hour,
    minute, second, and weekday.
    Attributes:
        _year: An integer of year.
        _month: An integer of month.
        _day: An integer of day.
        _hour: An integer of hour.
        _minute: An integer of minute.
        _second: An integer of second.
        _weekday: An integer of weekday.
    """
    def __init__(self,year=1911,month=1,day=1,hour=0,minute=0,second=0):
        self._Set(year,month,day,hour,minute,second)
    def __add__(self,arg):
        if(type(arg)==int):
            """The arg is seconds at this stage"""
            this=datetime.datetime(*self.ToList())
            buf=this+datetime.timedelta(seconds=arg)
            new_time_info=FKLTimeInfo()
            new_time_info.ReSet(buf.year,buf.month,buf.day,buf.hour,buf.minute,buf.second)
            result=new_time_info
        else:
            raise Exception("FKLTimeInfo __add__ Error: The arg must be int.")
        return result
    def __radd__(self,arg):
        if(type(arg)==int):
            """The arg is seconds at this stage"""
            this=datetime.datetime(*self.ToList())
            buf=this+datetime.timedelta(seconds=arg)
            new_time_info=FKLTimeInfo()
            new_time_info.ReSet(buf.year,buf.month,buf.day,buf.hour,buf.minute,buf.second)
            result=new_time_info
        else:
            raise Exception("FKLTimeInfo __radd__ Error: The arg must be int.")
        return result
    def __sub__(self,arg):
        if(type(arg)==FKLTimeInfo):
            """The arg is class FKLTimeInfo at this stage"""
            this=datetime.datetime(*self.ToList())
            another=datetime.datetime(*arg.ToList())
            result=int((this-another).total_seconds())
        elif(type(arg)==int):
            """The arg is seconds at this stage"""
            this=datetime.datetime(*self.ToList())
            buf=this-datetime.timedelta(seconds=arg)
            new_time_info=FKLTimeInfo()
            new_time_info.ReSet(buf.year,buf.month,buf.day,buf.hour,buf.minute,buf.second)
            result=new_time_info
        else:
            raise Exception("FKLTimeInfo __sub__ Error: The arg must be FKLTimeInfo or int.")
        return result
    def __rsub__(self,arg):
        if(type(arg)==FKLTimeInfo):
            """The arg is class FKLTimeInfo at this stage"""
            this=datetime.datetime(*self.ToList())
            another=datetime.datetime(*arg.ToList())
            result=int((another-this).total_seconds())
        elif(type(arg)==int):
            """The arg is seconds at this stage"""
            this=datetime.datetime(*self.ToList())
            buf=this-datetime.timedelta(seconds=arg)
            new_time_info=FKLTimeInfo()
            new_time_info.ReSet(buf.year,buf.month,buf.day,buf.hour,buf.minute,buf.second)
            result=new_time_info
        else:
            raise Exception("FKLTimeInfo __rsub__ Error: The arg must be FKLTimeInfo or int.")
        return result
    def _Set(self,year,month,day,hour,minute,second):
        try:
            date_info_buf=datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second))
        except Exception as error_str:
            raise Exception("FKLTimeInfo _Set Error: "+str(error_str)+".")
        self._year=date_info_buf.year
        self._month=date_info_buf.month
        self._day=date_info_buf.day
        self._hour=date_info_buf.hour
        self._minute=date_info_buf.minute
        self._second=date_info_buf.seconds
        self._weekday=datetime.date(self._year, self._month, self._day).weekday()+1
    def ReSet(self,year=1911,month=1,day=1,hour=0,minute=0,second=0):
        self._Set(year,month,day,hour,minute,second)
    def ToList(self):
        return [self._year,self._month,self._day,self._hour,self._minute,self._second]
    def ToStr(self):
        year_str=str(self._year)
        if(self._month<10):month_str="0"+str(self._month)
        else:month_str=str(self._month)
        if(self._day<10):day_str="0"+str(self._day)
        else:day_str=str(self._day)
        if(self._hour<10):hour_str="0"+str(self._hour)
        else:hour_str=str(self._hour)
        if(self._minute<10):minute_str="0"+str(self._minute)
        else:minute_str=str(self._minute)
        if(self._second<10):second_str="0"+str(self._second)
        else:second_str=str(self._second)
        return year_str+month_str+day_str+hour_str+minute_str+second_str
    def Year(self):
        return self._year
    def Month(self):
        return self._month
    def Day(self):
        return self._day
    def Hour(self):
        return self._hour
    def Minute(self):
        return self._minute
    def Second(self):
        return self._second
    def Weekday(self):
        return self._weekday

def FKLStr2TimeInfo(string):
    """
    Args:
        string: A string of 14 dimentional number that represent a certain times.
    Returns:
        Return a object of FKLTimeInfo.
    Raises:
        Exception: The string len must be 14.
    """
    string=re.sub("[^0-9]","",string)
    if(len(string)!=14):raise Exception("FKLStr2TimeInfo Error: The string len must be 14.")
    year=int(string[:4])
    month=int(string[4:6])
    day=int(string[6:8])
    hour=int(string[8:10])
    minute=int(string[10:12])
    second=int(string[12:14])
    return FKLTimeInfo(year,month,day,hour,minute,second)
def FKLGetCurrentTimeStr():
    return time.strftime("%Y%m%d%H%M%S",time.localtime())
def FKLGetCurrentTimeInfo():
    return FKLStr2TimeInfo(FKLGetCurrentTimeStr())