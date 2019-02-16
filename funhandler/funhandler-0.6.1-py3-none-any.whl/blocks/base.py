from abc import ABC
import uuid
import threading
from multiprocessing import Queue as MQueue

class Addable(ABC):
    def __init__(self):
        pass

class BaseBlock(Addable):
    """
        Blocks work a lot like Environments inside for reinforcement learning.
        A block has the following:
            - step
                - The step function iterates through all of the proper states and modifies them according to a given action
            - 
    """
    def __init__(self, name, type_name, **kwargs):
        self.name = name
        self.type_name = type_name
        self.required = [] # Set a list of required types that need to be added
        self.current_id = str(uuid.uuid4())

    def __call__(self, **kwargs):
        """ Will get all of the requirements of each object and try setting unfilled requirements from the main state"""
        raise NotImplementedError

    
    def check_required(self):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError

    def add_requirements(self, *args):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError
    
    def reset(self):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError

    def step(self, action, **kwargs):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError
    

    def __repr__(self):
        capname = self.type_name.capitalize()
        return "<{0} 0x:{2} -- {1}>".format(capname, self.name, self.current_id)

class Env(BaseBlock):
    def __init__(self, name, type_name, is_world=False, world=None, world_config={}, **kwargs):
        self.name = name
        self.type_name = type_name
        self.required = [] # Set a list of required types that need to be added
        self.current_id = str(uuid.uuid4())

    def __call__(self, **kwargs):
        """ Will get all of the requirements of each object and try setting unfilled requirements from the main state"""
        raise NotImplementedError

    
    def check_required(self):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError

    def add_requirements(self, *args):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError
    
    def reset(self):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError

    def step(self, action, **kwargs):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError
    

    def __repr__(self):
        capname = self.type_name.capitalize()
        return "<{0} 0x:{2} -- {1}>".format(capname, self.name, self.current_id)

class StateBlock(BaseBlock):
    """
        This block is used to save and store states. The state is usually to store information about what the session will need
    """
    def __init__(self, name, type_name, **kwargs):
        self.name = name
        self.type_name = type_name
        self.required = [] # Set a list of required types that need to be added
        self.current_id = str(uuid.uuid4())

    def __call__(self, **kwargs):
        """ Will get all of the requirements of each object and try setting unfilled requirements from the main state"""
        raise NotImplementedError

    
    def check_required(self):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError

    def add_requirements(self, *args):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError
    
    def reset(self):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError

    def step(self, action, **kwargs):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError
    

    def __repr__(self):
        capname = self.type_name.capitalize()
        return "<{0} 0x:{2} -- {1}>".format(capname, self.name, self.current_id)


class ActionBlock(BaseBlock):
    """
        This block is used to save and store states. The state is usually to store information about what the session will need
    """
    def __init__(self, name, type_name, **kwargs):
        self.name = name
        self.type_name = type_name
        self.required = [] # Set a list of required types that need to be added
        self.current_id = str(uuid.uuid4())

    def __call__(self, **kwargs):
        """ Will get all of the requirements of each object and try setting unfilled requirements from the main state"""
        raise NotImplementedError

    
    def check_required(self):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError

    def add_requirements(self, *args):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError
    


    def action_filter(self):
        raise NotImplementedError
    
    def reset(self):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError

    def step(self, action, **kwargs):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError
    

    def __repr__(self):
        capname = self.type_name.capitalize()
        return "<{0} 0x:{2} -- {1}>".format(capname, self.name, self.current_id)

class InfoBlock(Addable):
    """
        This block is used to add default information to the sessions object.

        Example: PortfolioBacktest() - Will add the following:
            - Portfolio
            - Object Store
            - PortfolioEnvironment
            - Estimators
        
        Those objects, with default values, will be added to the session at runtime
    """
    def __init__(self, name, type_name, **kwargs):
        self.name = name
        self.type_name = type_name
        self.required = [] # Set a list of required types that need to be added
        self.current_id = str(uuid.uuid4())

    def __call__(self, **kwargs):
        """ Will get all of the requirements of each object and try setting unfilled requirements from the main state"""
        raise NotImplementedError

    
    def check_required(self):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError

    def add_requirements(self, *args):
        """ Checks for required objects. Usually understood by checking types """
        raise NotImplementedError
    


    def action_filter(self):
        raise NotImplementedError
    
    def reset(self):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError

    def step(self, action, **kwargs):
        # Run the execute when the run function is run for the session. 
        raise NotImplementedError
    

    def __repr__(self):
        capname = self.type_name.capitalize()
        return "<{0} 0x:{2} -- {1}>".format(capname, self.name, self.current_id)


class StoreBlock(Addable):
    """
        This block is used to store states of an application. Can use different backends for this block model
    """
    def __init__(self, name, type_name, **kwargs):
        self.name = name
        self.type_name = type_name
        self.required = [] # Set a list of required types that need to be added
        self.current_id = str(uuid.uuid4())

    def add(self, *args, **kwargs):
        """ Adds a group of objects into a serialized file. Kwargs are search parameters for the user """
        raise NotImplementedError
    
    def get(self, **kwargs):
        """ 
            Get all of the objects stored by the given search parameters kwargs. 
            If nothing is in the database. It'll return a dict with none in the data column.
            Otherwise: It'll return a dict with something in the column
        """
        raise NotImplementedError
    





"""
    Action Block:
    
    dispatch = DispatchOrder()
    dispatch.step(buy, trade="BTC", base="USDT", exchange="binance") # returns a general portfolio and dispatches to everything
"""
