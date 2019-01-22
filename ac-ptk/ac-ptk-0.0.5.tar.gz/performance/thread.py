import threading

from performance.android import AndroidApp


class PTKThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        assert isinstance(app, AndroidApp)
        self.app = app
        self.flag_stop = False

    def stop(self):
        self.flag_stop = True