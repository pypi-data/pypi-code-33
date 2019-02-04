import threading

class FKLThreadLock:
    def __init__(self):
        self._lock=threading.Lock()
    def Acruire(self):
        self._lock.acquire()
        return
    def Release(self):
        self._lock.release()