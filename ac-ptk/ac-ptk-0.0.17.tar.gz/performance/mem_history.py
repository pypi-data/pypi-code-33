
from performance import TODAY, TIME


class History(object):

    def __init__(self):
        self.avg = 0
        self.max = 0
        self.date = TODAY
        self.gmt_create = "%s-%s" % (TODAY, TIME)
        self.success = False
        self.device = ''
        self.pkg = ''
