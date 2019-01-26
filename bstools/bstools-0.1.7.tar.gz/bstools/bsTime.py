#coding = utf-8

import time

__all__ = ["tsToLt", "PerformCacl", "ltToTs"]

def performCacl(func):
    def main(*argv, **keys):
        timeStart = time.time()
        result = func(*argv, **keys)
        timeEnd = time.time()
        print(u"模块%s耗时: %.15f秒"%(func.__name__,timeEnd - timeStart))
        return result
    return main

def tsToLt(timestamp, timeType = "ms"):
    if timeType not in ["ms","s"]:
        raise bsTimeArrErr("参数错误, 接受'ms' 和's' ")
    else:
        tType = timeType
    timestamp = float(timestamp) if timeType == "s" else float(timestamp)*0.001
    timeArray = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

def ltToTs(timeString, timeType = "s"):
    try:    
        timeArray = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
    except ValueError:
        raise bsTimeFormatErr(u"时间字符串不正确, 请参考格式%Y-%m-%d %H:%M:%S")
    if timeType == "ms":
        timeStamp = timeStamp * 1000
    elif timeType == "s":
        pass
    else:
        raise arrTypeErr(u"参数错误, 接受'ms' 和's' ")
    return timeStamp

class bsTimeFormatErr(Exception):
    def __init__(self, *args):
        self.args = args    
        
class bsTimeArrErr(Exception):
    def __init__(self, *args):
        self.args = args    