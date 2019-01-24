# coding=utf-8

import threading, time
from .Utils import MyLogger

class ThreadRets(object):
    def __init__(self):
        self._rets = {}

    def addRet(self, key, val):
        assert isinstance(key, basestring), \
            'isinstance(key, basestring), but type(key)={}'.format(type(key))
        self._rets[key] = val

    def lenRets(self):
        return len(self._rets)

    def rets(self):
        return self._rets


@staticmethod
def threadsRun(runOneFn, runOneKwargsDict, timeoutSum=50, name='', ifRaiseTimeout=True, __ThreadGap__=0.5):
    """ exam:
    threadsRun(httpjson_post, runOneKwargsDict={
        "item_id_1": {reqUrl=Url_Ex+"/testAnItem_FastAudit",reqJson=dict(item_id="item_id_1",item_type="kVideoSet4Many")},
        "item_id_2": {reqUrl=Url_Ex+"/testAnItem_FastAudit",reqJson=dict(item_id="item_id_1",item_type="kVideoSet4Many")}
    })

    """
    __ThreadRets__ = ThreadRets()
    threads = {}
    _names = runOneKwargsDict.keys()
    _num = len(_names)
    for i in range(_num):
        _name = _names[i]
        runOneKwargs = runOneKwargsDict[_name]
        runOneKwargs.update(dict(__ThreadRets__=__ThreadRets__, __ThreadName__=_name, __ThreadGap__=__ThreadGap__ * i))
        threads[_name] = threading.Thread(
            name=_name,
            target=runOneFn,
            kwargs=runOneKwargs
        )
    for _name, t in threads.items():
        t.setDaemon(True)
        t.start()

    _timeSum = timeoutSum + (__ThreadGap__ * _num)
    _timeLogGap = int(_timeSum / 100.0) or 1
    for sec in range(1, int(1 + timeoutSum + (__ThreadGap__ * _num))):
        if __ThreadRets__.lenRets() == len(threads) or (not len([t for note, t in threads.items() if t.isAlive()])):
            break
        time.sleep(1)
        if sec % 10 == 0:
            MyLogger.logDbg('--><{}>: threadsRun({}): ({}/<{}+{}*{}>)s'.format(threading.current_thread().name, name, sec,
                                                                           timeoutSum, __ThreadGap__, _num))
    else:
        if ifRaiseTimeout:
            raise Exception('threadsRun timeout')
    return __ThreadRets__.rets()

