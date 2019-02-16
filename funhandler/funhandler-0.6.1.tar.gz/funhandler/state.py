"""
    This is a shares state object. 
    
    Using this object we're able to add items to monitor throughout the iterations

"""

from operator import add
import threading
import uuid
import random
import multiprocessing


class MainState(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.globalState = {}
    
    def dispatch(self, **kwargs):
        """ Add state item """
        with self.lock:
            for k ,v in kwargs.items():
                self.globalState[k] = v
    
    def get(self, key):
        with self.lock:
            try:
                k = self.globalState[key]
                return k
            except Exception as e:
                raise AttributeError("Key not found")



# TODO: Please complete
class StepProxy(object):
    def __init__(self, *args):
        """
            Contains all of the simulation references and updates the steps manually between threads
        """
        if len(args) != 0:
            pass
        pass
    
    

    
    


class Pizza(object):
    def __init__(self, **kwargs):
        self._id = uuid.uuid4()
        gstate = kwargs.get("gstate", None)
        
        if gstate is None:
            raise AttributeError("Global state not provided")
        
        self.gstate = gstate
        self.queue = multiprocessing.Queue()

    def random_choice(self):
        return random.choice([1, 2, 3])

    def update(self):
        # Gets from the outside state what the last action
        num = self.gstate.get("num")
        if num == 1:
            print("red")
        elif num == 2: 
            print("Green")
        elif num == 3:
            print("Blue")
        else:
            print("I don't know what to do")
if __name__ == "__main__":

    st = MainState()
    st.dispatch(num=1)

    pizza1 = Pizza(gstate=st)
    pizza2 = Pizza(gstate=st)
    pizza3 = Pizza(gstate=st)

    pizza_list = [pizza1, pizza2, pizza3]

    for p in pizza_list:
        p.update()