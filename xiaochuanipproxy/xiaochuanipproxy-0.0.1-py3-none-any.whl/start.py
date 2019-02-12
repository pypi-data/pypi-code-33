import filter
import threading

def fun_timer():        #定时器，每隔1800秒更新一次ip
    filter.updateip()
    global timer
    timer = threading.Timer(1800,fun_timer)
    timer.start()

def start():
    '''
    开始整个程序
    :return:
    '''
    timer = threading.Timer(1,fun_timer)
    timer.start()