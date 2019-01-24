import kthread
try:
	import thread
except ImportError:
	import _thread as thread
import threading
import time

name = "bombfuse"

def timeout(sec, func = None, *args, **kwargs):
    """Executes a function, raising a KeyboardInterrupt exception in the main thread after sec seconds have elapsed"""
    
    def timeout_thread():
        for i in range(0, sec):
            time.sleep(1)
        thread.interrupt_main()
        
    def timeout_block():
        ret = None
        try:
            y = kthread.KThread(target = timeout_thread)
            y.daemon = True
            y.start()
            if func is not None:
                ret = func(*args, **kwargs)
                if y.isAlive() == True:
                    try:
                        y.kill()
                    except Exception as e:
                        # thread already stopped?
                        pass
                return ret
            else:
                if y.isAlive() == True:
                    try:
                        y.kill()
                    except Exception as e:
                        # thread already stopped?
                        pass
        finally:
            if y.isAlive() == True:
                try:
                    y.kill()
                except Exception as e:
                    pass
            return ret
            
    if sec is None or sec == 0:
        if func is not None:
            return func(*args, **kwargs)
        else:
            return None
            
    return timeout_block()