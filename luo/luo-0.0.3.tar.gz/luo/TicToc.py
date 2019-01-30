import time
import datetime

'''
    This file will realize some function about time
'''

def format_time():
    '''
        return format time %Y-%m-%d %H:%M:%S.%f.3
    '''
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class TicToc(object):
    def __init__(self):
        self.total_time = 0
        self.calls = 0
        self.start_time = 0
        self.diff = 0
        self.average_time = 0
    
    def tic(self):
        self.start_time = time.time()
    
    def toc(self, average=True):
        self.diff = time.time() - self.start_time
        self.total_time += self.diff
        self.calls += 1
        self.average_time = self.total_time / self.calls
        if average:
            return self.average_time
        else:
            return self.diff

if __name__ == "__main__":
    tictoc = TicToc()
    tictoc.tic()
    time.sleep(1)
    print(tictoc.toc())
    print(format_time())

    