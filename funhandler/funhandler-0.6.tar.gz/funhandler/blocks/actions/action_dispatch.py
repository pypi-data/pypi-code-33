from random import choice
import random
import numpy as np
import ray
from loguru import logger
from ray.actor import ActorHandle, ActorClass
from ray.remote_function import RemoteFunction

from funhandler.blocks import ActionBlock, StateBlock

ray.init()
logger.level("STEP", no=15, color="<green>", icon="🐍")

class DispatchOrder(ActionBlock):
    def __init__(self, name, **kwargs):
        super().__init__(name, "dispatchorder", **kwargs)
        self.dispatch_type = kwargs.get("dispatch_type", "loop")
        self.required_objects = {}
        self.settings = {
            "portfolio": {
                "remote": False
            }
        }
        self.add_requirements("portfolio")
        self.add_required(**kwargs)



    def __call__(self, **kwargs):
        self.add_required(**kwargs)
        
    def add_required(self, **kwargs):
        portfolio = kwargs.get("portfolio")
        rkeys = self.required_objects.keys()
        if portfolio is not None:
            logger.opt(ansi=True).info("Adding a <r>portfolio</r>")
            if "portfolio" not in rkeys:
                p = portfolio
                if isinstance(portfolio, ActorClass):
                     p = portfolio.remote()
                     self.settings["portfolio"]["remote"] = True
                elif isinstance(portfolio, ActorHandle):
                    self.settings["portfolio"]["remote"] = True
                else:
                    pass
                self.required_objects["portfolio"] = p

    def add_requirements(self, *args):
        # Maybe push requirement of having a portfolio object included
        for a in args:
            if isinstance(a, str):
                self.required.append(a)
    
    def check_required(self):
        rkeys = self.required_objects.keys()
        for _ in self.required:
            if _ not in rkeys:
                raise AttributeError("{} not added".format(_))
    
    def action_filter(self):
        logger.debug("Action Filter")

    def reset(self):
        logger.info("<g>Checking</g> for requirements")
        self.check_required()
        # logger.debug("Reset Dispatcher")

    def error_responses(self, _type, **kwargs):
        if _type == "missing":
            name = kwargs.get("vname")
            message = "{} variable not added".format(name)
            raise AttributeError(message)

    def step(self, action, **kwargs):
        pct = kwargs.get("pct")
        base = kwargs.get("base")
        trade = kwargs.get("trade")
        exchange = kwargs.get("exchange")

        if pct is None:
            self.error_responses("missing", vname="Pct")
        if base is None:
            self.error_responses("missing", vname="Base")
        if trade is None:
            self.error_responses("missing", vname="Trade")

        if exchange is None:
            self.error_responses("missing", vname="Exchange")


        msg = """<y>Action:</y>{action}\t<y>Pair:</y>{base}-{trade}-{exchange}""".replace("\n", " ")

        logger.opt(ansi=True).debug(
            msg, 
            action=action, 
            base=base, 
            trade=trade, 
            exchange=exchange
        )
        if self.dispatch_type == "loop":
            # Turn this into a single object
            logger.log("STEP", "Send orders to function (celery)") # add to required functions
            logger.log("STEP", "\t- Get all users that need to be ordered in")
            logger.log("STEP", "\t- Check if user's are enabled")
            logger.log("STEP", "\t- Send to order server")
            logger.log("STEP", "\t\t- Dispatch to monitor system (monitor feedback loop)")
            logger.log("STEP", "Send orders to local portfolio")
            logger.log("STEP", "\t- Make changes to local portfolio (accessible using ray)")
            logger.log("STEP", "\t- return the state of the local portfolio")
            portfolio = self.required_objects["portfolio"]
            poop = portfolio.step.remote(action)
            results = ray.get(poop)
            logger.debug(results)


@ray.remote
class Portfolio(object):
    def __init__(self):
        pass
    
    def save(self):
        print("Saving Portfolio")
        # print("Saving Portfolio")
    
    def load(self):
        print("Loading Portfolio")

    def step(self, action):
        self.load()
        balance = random.uniform(1, 10000)
        shares = {"BTC": random.uniform(1, 10000), "USDT": random.uniform(1, 10000), "ETH": random.uniform(1, 100)}
        holdings = {}
        self.save()
        return balance, shares, holdings
    
@ray.remote
def remote_func(a, b):
    return a+b



if __name__ == "__main__":
    # portfolio = Portfolio.remote()
    # print(type(remote_func))
    # print(type(Portfolio))
    dispatch = DispatchOrder("Live Dispatcher", portfolio=Portfolio)
    dispatch.reset()
    for i in range(10):
        order_choice = choice(["buy", "sell", "hold"])
        order_pct = np.random.beta(1,2)
        base="USDT"
        trade=choice(["ETH", "BTC", "ETC", "DASH"])
        exchange=choice(["binance", "bittrex", "huboi"])
        dispatch.step(
            order_choice, 
            pct=order_pct, 
            base=base, 
            trade=trade, 
            exchange=exchange
        )
    
    print(dispatch)