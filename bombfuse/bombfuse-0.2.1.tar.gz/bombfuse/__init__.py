import exceptions
import kthread
try:
	import thread
except ImportError:
	import _thread as thread
import time

name = "bombfuse"

class TimeoutError(exceptions.KeyboardInterrupt):
    def __init__(self, func = None):
        self.func = func
        super(TimeoutError, self).__init__()
            
    def __str__(self):
        if self.func is not None:
            return "The function '{}' timed out".format(self.func.__name__)
        else:
            return "The function timed out"

def timeout(sec, func = None, *args, **kwargs):
    """Executes a function, raising an exception in the main thread after sec seconds have elapsed"""
    
    def timeout_thread():
        timed_out = False
        try:
            t0 = time.time()
            while True:
                t1 = time.time()
                if t1 - t0 >= sec:
                    timed_out = True
                    break
                time.sleep(0.2)
        finally:
            if timed_out == True:
                thread.interrupt_main()
            else:
                thread.exit()
        
    def timeout_block():
        try:
            y = kthread.KThread(target = timeout_thread)
            y.daemon = True
            y.start()
            return func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            while y.isAlive() == True:
                y.kill()
                y.join()
            
    if sec is None or sec == 0:
        if func is not None:
            return func(*args, **kwargs)
        else:
            return None
            
    try:
        return timeout_block()
    except KeyboardInterrupt as e:
        e = TimeoutError(func)
        raise e
    except Exception as e:
        raise e