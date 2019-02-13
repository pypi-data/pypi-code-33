from queue import Queue, Full


class EventQueue(object):
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.queue = Queue(self.maxsize)

    def get(self, timeout):
        return self.queue.get(block=True, timeout=timeout)

    def get_nowait(self):
        return self.queue.get_nowait()

    def put(self, item):
        pushed = False
        while pushed is False:
            try:
                self.queue.put_nowait(item)
                pushed = True
            except Full:
                try:
                    self.queue.get_nowait()
                    self.queue.task_done()
                except Empty:
                    pass

event_queue = EventQueue(200)
