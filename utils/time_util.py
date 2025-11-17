import datetime
import time


def TtimeStamp_Time(timeStamp):
    """时间戳转化为时间字符串
    Args:
        timeStamp (int): 时间戳
    Returns:
        str: 时间字符串
    """
    timeStamp = int(str(timeStamp)[0:10])
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime  # 2013--10--10 23:40:00


def timeStamp(min):
    """现在时间转化为13位置时间戳  min----加减时间
    Args:
        min (_type_): _description_
    Returns:
        _type_: _description_
    """    
    x = (datetime.datetime.now()+datetime.timedelta(minutes=min)).strftime("%Y-%m-%d %H:%M:%S")
    timeArray = time.strptime(x, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray)) * 1000
    return timestamp



def UTC_TtimeStamp_Time(min):
    """UTC时间转化为 应用格式：min----加减时间，2022-09-07T02:23:02.790Z
    Args:
        min (_type_): _description_
    Returns:
        _type_: _description_
    """
    UTCtime = datetime.datetime.utcnow()+datetime.timedelta(minutes=min)
    otherStyleTime = UTCtime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return otherStyleTime
