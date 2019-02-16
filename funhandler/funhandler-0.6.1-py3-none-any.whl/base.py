import sys
import uuid
import random

from distributed.worker import thread_state
from funtime import Store, Converter
# this is a pointer to the module object instance itself.
this = sys.modules['funhandler']
# Use these variables to handle the database


def set_host(host):
    if (this.host is None):
        # also in local function scope. no scope specifier like global is needed
        this.host = host
    else:
        print(f"Database is already initialized to {this.host}.")

def set_store_name(store_name):
    this.store_name = store_name

def initialize_database():
    """
        Globally set the database here
    """
    # TODO: Refactor the funtime library
    this.db = Store(this.host).create_lib(this.store_name).get_store()

def get_db_params():
    return {
        "host": this.host,
        "store_name": this.store_name,
        "db": this.db,
    }

def set_file_storage(source='local', **kwargs):
    """ Creates file storage depending

    Parameters
    ----------
    source: str
        Default is 'local' which will create
        file storage in the local environment
    kwargs: dict
        Contains data to setup S3 storage
    """
    pass


# class Handler(object):
#     def __init__(self):
#         pass

#     def generate_stochastic_episodes(self, 
#                                     episode_number=10, 
#                                     types_per_episode=['gbm', 'jump_diff'], 
#                                     number_per_episode=10000):
#         """ Generate a local set of stochastic episodes """
#         pass

#     def get_episodes(self):
#         return []


#     def pop_session(episode_id=None):
#         return []
    
#     def is_sessions(self, episode_id):
#         return True

#     def is_session(self, session_id):
#         return True
    
#     def pop_data(self, session_id):
#         return random.randint(1, 100)

    


# TODO: Set storage location eventually too for the parkquet file
