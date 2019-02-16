import uuid
import numpy as np
from abc import ABC, abstractmethod
from loguru import logger
from funhandler.blocks import BaseBlock, Addable, Env
# import ray
# ray.init()
# TODO: Place generators into a separate location. The generators should be in a separate place. 
# For example: We can place multiple generator blocks to get the AI to handle various types of distributions
# TODO: This is the environmeny 
class PlanetEconomy(Env):
    def __init__(self, name, **kwargs):
        super().__init__(name, "environment", **kwargs)
        # Embed world into the trading env through the kwargs
        # The world will hodl the communication structure as well as who has communicated recently 
        self.required = ['store'] # this needs to also include a generator functio
        # We're emulating action space dictionary
        self.actions = [-1, 0, 1] # hold, buy, sell 

        
        # NOTE: Commenting out action percentages for now to allow for
        # self.action_pct = np.linspace(0, 101) # how much of the portfolio we want to buy or sell.
        
        # The task parts are there to access for the dependency scheduler
        self.task_parts = {}

    def reset(self, agents):
        # self.check_required()
        logger.opt(ansi=True).debug("<m>{tasks}</m>", tasks=self.task_parts)
        # Get the portfolio and reset everything here
        # Get the the overall number of dimensions of the portfolio here
        # Convert the portfolio into a state (vector based decision)

        return np.array([np.zeros(1,)])
    
    def check_required(self):
        kwkeys = self.task_parts.keys()
        for i in self.required:
            if i not in kwkeys:
                msg = "{} not found in {}".format(i, self.__repr__())
                raise AttributeError(msg)
        

    def add_task_parts(self, parts):
        if isinstance(parts, dict):
            # print(parts_dict)
            total = {**self.task_parts, **parts}
            self.task_parts = total
    
    def step(self, action, **kwargs):
        # Step through a series of actions
        # Get the next_state, reward, done, _

        return 100, 9000, 10000, 20000
    

if __name__ == "__main__":
    planet = PlanetEconomy("worldtree", is_word=True, world={}, world_config={})
    planet.reset([
    {
        "name": "yaggal", 
        "role": "greenbank1", 
        "resources": {
            # Define a resource pool here
        }
    }, 
    {
        "name": "smeebly", 
        "role": "greenbank2", 
        "resources": {
            # Define a resource pool here
        }
    },
    {
        "name": "schmeckles", 
        "role": "greenbank3", 
        "resources": {
            # Define a resource pool here
        }
    }
    ])
    results = planet.step({
        'yaggal': {
            "trees": (0, 400, 1000),
            "espliquidity": (1, 300, 200)
        }, 
        "smeebly": {
            "trees": (0, 400, 1000),
            "espliquidity": (1, 300, 200)
        },
        "schmeckles": {
            "trees": (0, 400, 1000),
            "espliquidity": (1, 300, 200)
        },
    })
    
    logger.info(results)
    