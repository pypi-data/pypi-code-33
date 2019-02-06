"""
This module implements the logic for abstracting the 
tacyt clients of a threadpool.
"""

from multiprocessing import Pool

class TacytAppThreadPool:
    """
    This class wraps a TacytApp and forwards the method 
    invocations to the processes in the pool
    """
    
    def __init__(self, api, pool_size):
        self.wrapped_api = api
        self.pool_size = pool_size
        self.pool = Pool(processes=pool_size)

    def __getattr__(self, name):
        """
        Will be executed during the name lookup, it will look 
        for the method in the delegate and will forward
        the execution to it in a separate thread in the pool.
        """
        if hasattr(self.wrapped_api, name):
            def handler(*args, **kwargs):
                method = getattr(self.wrapped_api, name)
                # Will block execution until got result
                return self.pool.apply(method, args, kwargs)
                
            return handler
        else:
            raise AttributeError
