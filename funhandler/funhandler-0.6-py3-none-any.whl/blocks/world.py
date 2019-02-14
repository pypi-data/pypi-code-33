from loguru import logger
import random
import uuid
class Action(object):
    def __init__(self, *args, **kwargs):
        self.c = None # communication
        self.p = None # Buy/Sell
        self.s = None # Support/Unsupport
        self.g = None # The ability to grow the supply of a the coin (with limits)


class Entitiy(object):
    def __init__(self):
        self.state = None


class Property(object):
    def __init__(self):
        pass
    

# What international-banking like behavior can we build to make global warming production


class Agent(Entitiy):
    def __init__(self):
        pass

class WorldBank(Agent):
    def __init__(self, action_space=None):
        self.action_space = action_space
        self._id = str(uuid.uuid4())
    
    def act(self, world, policy_action):
        logger.opt(ansi=True).info("Choosing Action: <r>{}</r>", policy_action)
        world.energy_gen += 1

        # logger.debug("Take action")

class Location(Entitiy):
    def __init__(self):
        pass
        

class World(object):
    def __init__(self):
        self.agents = None
        self.locations = None
        self.passive = None

        self.energy = None
        self.energy_gen = None # The amount of energy used per step
        self.polution = None
        self.polution_gen = None
        self.settings = {
            "bank_num": 0
        }
    

    @property
    def entities(self):
        return self.agents


    @property
    def policy_agents(self):
        return [x for x in self.agents if x.action_space is not None]


    def set_settings(self, settings):
        if not isinstance(settings, dict):
            raise AttributeError("Setting incorrect type") 
        for i in settings.keys():
            self.settings[i] = settings[i]


    @property
    def get_actions(self):
        actions = []
        for age in self.policy_agents:
            actions.append(
                {
                    "id": age._id, 
                    "acts": {
                        "loan": {
                            "is": random.choice([True, False]),
                            "pct": random.uniform(0, 100)
                        },
                        "communicate": {
                            "is": random.choice([True, False]),
                            "pct": random.uniform(80, 100)
                        }
                    }
                }
            )
        return actions


    def reset(self, pagents=None):
        self.agents = []
        self.locations = []
        self.passive = []

        self.energy = 100
        self.energy_gen = 0 # The amount of energy used per step
        self.polution = 1000
        self.polution_gen = 0
        if pagents is None:
            raise EnvironmentError("No policy agents added")

        for i in pagents:
            self.agents.append(i)
        
        return self.get_actions
    

    def get_agent(self, _id):
        for i in self.agents:
            if _id == i._id:
                return i


    def learn(self, state, _state):
        logger.info("Learning")

    def step(self, action_list):
        # logger.opt(ansi=True).debug("Taking next step")
        for action in action_list:
            _ = self.get_agent(action["id"])
            _.act(self, action)

        logger.opt(ansi=True).debug("Energy generation per step: {}", world.energy_gen)
        
        return self.get_actions, 0, 0, random.choice([False, False, False, False, False, False, False, False, False, False, False, False, False, False,False, False, False, False, False, True])
        



# How the world will work
#   - Create a bunch of agents (machine learning models that will act)
#   - Each agent will have something they can take control of
#       - Monetary Supply
#       - Stimulation
#           - Infrastucture
#           - Services
#   On top of that, each agent will be able to communicate with other agents to collaborate
#   Therefore the available actions will have the following attributes:
#   - Communicate
#   - BUY|SELL|HOLD
#   - This will be a coin
#       - The coin will be in USD value
#   - SUPPORT|UNSUPPORT

# There will be two kinds of agents:
#   - Policy Agents
        # - They have an action callback
#   - ABCE Agents
        # - They dont they're controlled by script. No action callback
#   - We will add agents to the world at the very beginning of a world's creation

# Every step the passive entities will carry out a general command based on the observed state, then push their changes to the world.
def get_actions(agents):
    actions = []
    for age in agents:
        actions.append(
            {
                "id": age._id, 
                "acts": {
                    "loan": {
                        "is": random.choice([True, False]),
                        "pct": random.uniform(0, 100)
                    },
                    "communicate": {
                        "is": random.choice([True, False]),
                        "pct": random.uniform(80, 100)
                    }
                }
            }
        )
    return actions
def init_reinforcement(num=3):
    policy_list = []
    for i in range(num):
        policy_list.append(WorldBank(action_space=[]))
    
    return policy_list


if __name__ == "__main__":
    world = World()
    world.set_settings({
        'bank_num': 10
    })
    
    # Initializes reinforcement agents
    policy_agents = init_reinforcement(num=5)

    for i in range(100):    
        actions = world.reset(pagents=policy_agents)
        done = False
        while done == False:
            actions, state, _state, _done = world.step(actions)
            if done != True:
                world.learn(actions, state)
            done = _done

