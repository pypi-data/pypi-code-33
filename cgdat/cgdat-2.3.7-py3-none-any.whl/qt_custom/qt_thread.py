'''This module contains the classes and functions that are used qt gui to enable multithreading. It contains the
following components:
'''

### Set all ###
__all__ = ['WorkerSignals', 'Worker']

# Import qt modules
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Import other modules
import time
import traceback
import sys

###################################################################
### WorkerSignals Class                                         ###
###################################################################
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    ready
        `str` string specifying which worker was ready

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal(object)
    error = pyqtSignal(tuple)
    ready = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)

#####################################################################
### Worker Class                                                  ###
#####################################################################
# class Worker(QRunnable):
class Worker(QThread):
    '''Worker thread

    Inherits from QRunnable to handler worker thread setup, signals
    and wrap-up.

    Args:
        fn (callback): The function callback to run on this worker thread. The
                       supplied args and kwargs will be passed through to the runner.

        args (\*args): Arguments to pass to the callback function.

        kwargs (\*kwargs): Keywords to pass to the callback function.

    '''

    #################################################
    ### Class initiation                          ###
    #################################################
    def __init__(self, fn, *args, **kwargs):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Run QRunnable initialiser
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['ready_callback'] = self.signals.ready
        self.kwargs['progress_callback'] = self.signals.progress

    #################################################
    ### Class run function                        ###
    #################################################
    @pyqtSlot()
    def run(self):
        '''Retrieve args/kwargs and start up the thread using them.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
			# Run callback function
            result = self.fn(*self.args, **self.kwargs)
        except:
			# Send error signal
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
            result = (False,"thread_error")
        finally:

			# Send finished signal
            self.signals.finished.emit(result)
