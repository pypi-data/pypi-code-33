from abc import ABC
import uuid
import threading
import ray
from loguru import logger
from multiprocessing import Queue as MQueue
from funhandler.state import MainState
from funhandler.blocks import BaseBlock, StateBlock, Portfolio, Addable, MrayStorage
from funhandler.blocks.environments.trading import TradingEnvBuilder 



class Session(object):
    def __init__(self, name, **kwargs):
        """
            raystate: boolean
                - determines if the shared state is a ray actor. 
                - If it's true we set send calls (using ray calls),
                - Otherwise we push states to the Borg shared state
        """
        self.name = name
        self.lock = None
        self.global_items = {}

        logger.opt(ansi=True).info("Starting session store <r>{}</r>", self.name)
    
    def add_global_key(self, addable):
        global_keys = self.global_items.keys()
        addable_name = addable.type_name
        if addable_name not in global_keys:
            self.global_items[addable_name] = []
        # addable.reset()
        self.global_items[addable_name].append(addable)
        

    def add(self, addable):
        # Sets an addable object. Checks to be an instance of Session/Executable.
        if isinstance(addable, Addable):
            self.add_global_key(addable)
        else:
            logger.error("Not addable")
    
    def reset(self, **kwargs):
        """Resets a current object"""
        _type = kwargs.get("type", "all")
        
        logger.opt(ansi=True).info("<r>Resetting</r> the <c>session</c> <g>store</g>")
        global_keys = list(self.global_items.keys())
        if _type == "all":
            """ Reset everything. Should be used prior to running through simulations. """
            logger.opt(ansi=True).info("<y>Resetting everything</y>")
            logger.info(global_keys)
            for i in global_keys :
                items = self.global_items[i]
                for index, _ in enumerate(items):
                    if len(_.required) > 0:
                        e = self.get_requirement(_)
                        # logger.debug(e)
                        self.global_items[i][index].add_task_parts(e)
                    self.global_items[i][index].reset()
                    # _.reset()
            
        else:
            logger.info(global_keys)
            if _type not in global_keys:
                msg = "`{}` was not found".format(_type)
                raise AttributeError(msg)
    
    def get_requirement(self, obj):
        logger.opt(ansi=True).debug(obj)
        global_keys = list(self.global_items.keys())
        o = {}
        for req in obj.required:
            if req in global_keys:
                o[req] = self.global_items[req][0]
        return o
        



    def step(self, action, **kwargs):
        """

        """
        _type = kwargs.get("type", None)
        observation = 0
        reward = 0
        done = False
        info = {}
        name = kwargs.get("name", None)
        data = kwargs.get("data", None)
        logger.opt(ansi=True).info("<c>{}</c> action",action)


        if _type is None:
            raise AttributeError(" 'type' not added. Used to locate what kind of object we'd like to step through.")
        
        search_name = False
        
        if name is not None:
            logger.opt(ansi=True).info("Stepping with both type: <m>{}</m> and name: <g>{}</g>", _type, name)
            search_name = True
        else:
            logger.opt(ansi=True).info("Only stepping with type: <m>{}</m>", _type, name)
        
        
        if data is None:
            raise AttributeError("No data supplied. Please supply data to run this process.")
        
        if _type not in self.global_items.keys():
            raise AttributeError("Type doesn't exist in the global keys")
        

        if search_name is True:

            _type_list = self.global_items[_type]
            tlist = [x.name for x in _type_list]
            if name not in tlist:
                msg = "{} not in {} list".format(name, _type)
                raise AttributeError(msg)
            else:
                for item in self.global_items[_type]:
                    if item.name == name:
                        logger.info(item.step(action, **data))
        else:
            for item in self.global_items[_type]:
                logger.debug(item.step(action, **data))
        return observation, reward, done, info
                

                
    



if __name__ == "__main__":
    sess = Session("blank", live=False, training=True) # if it's a training system, it's reasonable to begin reasoning that we'll be training here
    sess.add(MrayStorage("blank"))
    sess.add(Portfolio("userportfolio"))
    sess.add(TradingEnvBuilder("tradeenv"))
    # TODO: Add reinforcement learning
    # TODO: Add a runner function here to both run through generators and various portfolios 
    sess.reset()


    # NOTE: We would place this into the strategy class. We'll call the reinforcement learning algo here 
    sess.step("Fuck You", type="environment", data={})
    # sess.reset(type="all")
    # for _ in range(100):
    #     sess.step("BUY", type="portfolio", name="userportfolio", data={})
    # sess.stop()




    """
        # Running a Q Learning Agent On a Portfolio
        ---
        
        Steps:
            1. Add the world
            2. Add Storage Option (ray and funtime for now)
            3. Add the environment
            4. Run through setup
            5. Add LearningAgent(s)
            6. Run second setup (to ensure the agents know how to act (action/observation spacing))

            ---

        Pseudo-Code:
            session = Session("environment-world", save=True)
            session.add(BarFeed(...))
            session.add(MrayStorage(unique_id=True)) # mongo ray storage
            session.add(Portfolio("portfolio-name"))
            session.add(TradingEnvBuilder("portfolio-specific"))
            session.add(SARSAAgent(), amount=3)
            session.reset() # reset does graph configuration. Task dependency setup using available data
            emission_list = session.emission_list() # gets the appropiate selectors to emit data in series

            # Example Emission Item Inside of Emission List (for trading):
            {
                "type": "train",
                "data": {
                    "model": {
                        "pairs": ["BTC_ETH", "USD_ETH"],
                        "portfolio": True
                    }
                    "agents": {
                        "type": "SARSA"
                    }
                }

            }

            # How training will work
            
            # Declare a strategy
            strategy = Strategy(sess=session)
            strategy.add(Indicator1(**indicator_params))
            strategy.add(Indicator2(**indicator_params))
            strategy.add(Indicator3(**indicator_params))
            for eitem in emission_list:
                strategy.step(eitem) # The strategy will get the necessary data (if compatible), preprocess, then step through the given session



            source = Stream()
            source.map(step_session).filter(is_done).sink(reemit)

            def main():
                for eitem in emission_list:
                    source.emit(eitem)
    """


    """
        How we'll organize the session steps:
            1. We use a task graph
            2. We determine the order of the task graph when we call session.reset()
            3. Every `step()` we run through the entire dask task graph
            4. At the end, we call the output.
                - This should be a dictionary explaining everything: Observarion, State, Done, etc
    """
    # Tests to run
    # Can I push an action to modify a state
