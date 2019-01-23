from threading import Lock

if False:
    from typing import Dict


class NoData(object):
    pass


def _args_for_lock(blocking, timeout):
    if blocking:
        args = (blocking, timeout)
    else:
        args = (blocking,)
    return args


class VariableSub(object):
    def __init__(self, pub):
        self.pub = pub
        self.lock = Lock()
        self.return_on_no_data = NoData()
        self.lock.acquire()
        self.name = hash(self)

    def get(self, blocking=False, timeout=0.0):
        if self.lock.acquire(*_args_for_lock(blocking, timeout)):
            data = self.pub.get_data(blocking, timeout)
        else:
            data = self.return_on_no_data
        return data

    def release(self):
        try:
            try:
                del self.pub.subs[self.name]
            except KeyError:
                pass
            self.lock.release()
        except RuntimeError:
            pass

    def __del__(self):
        self.release()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()



class VariablePub(object):
    def __init__(self):
        self.subs = {}  # type: Dict[VariableSub]
        self.__data = None
        self.__write_lock = Lock()

    def make_sub(self):  # type: ()->VariableSub
        sub = VariableSub(self)
        self.subs[sub.name] = sub
        return sub

    def publish(self, data, blocking=True, timeout=0.0, force_all_read=False):
        self.__set_data(data, blocking, timeout)
        for sub in self.subs.values():
            try:
                sub.lock.release()
            except RuntimeError:
                pass

    def get_data(self, blocking=False, timeout=0.0):
        self.__write_lock.acquire(*_args_for_lock(blocking, timeout))
        self.__write_lock.release()
        return self.__data

    def __set_data(self, new_data, blocking=True, timeout=0.0):
        self.__write_lock.acquire(*_args_for_lock(blocking, timeout))
        self.__data = new_data
        self.__write_lock.release()
