""" This models contains all the signals used by the library. """

from .utils.signal import Signal

all_signals = []
def __create_signal(name):
    global all_signals
    signal = Signal(name)
    all_signals.append(signal)
    return signal


#--- persistance ---------------------------------------------------------------
#: Signal is emitted when a persistance process is started.
#: 
#: :param item: the item that was used to persist the data.
#: :param item_structure: Dictionary with single item classes as keys and lists
#:     of single item instances as values.
before_db_persist = __create_signal('before_db_persist')

#: Signal is emitted when a persistance process is completed.
#: 
#: :param items: List of persisted items.
#: :param models: List of lists of persisted models corresponding to the list of
#:     items. One item can have more then one model updated.
after_db_persist = __create_signal('after_db_persist')
