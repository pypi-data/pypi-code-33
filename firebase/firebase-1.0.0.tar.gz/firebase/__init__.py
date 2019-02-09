import atexit

from .async_compatible import process_pool

from firebase import *

name = 'firebase'


@atexit.register
def close_process_pool():
    """
    Clean up function that closes and terminates the process pool
    defined in the ``async_compatible`` file.
    """
    process_pool.close()
    process_pool.join()
    process_pool.terminate()
