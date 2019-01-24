from .location_agent import LocationAgent
from .household_agent import HouseholdAgent

import random
from mesa.time import BaseScheduler


class HouseholdsFirstActivation(BaseScheduler):
    """ A scheduler which activates all household agents before activating
    the location agents. It rebuilds the r_tree in between the stages.
    """
    def __init__(self, model, agent_class=HouseholdAgent, location_class=LocationAgent):
        """ Create an empty HouseholdsFirstActivation Activation schedule.

        Args:
            model: Model object associated with the schedule.
            agent_class: The class of the household agents
            location_class: The class of the location agents
        """
        super().__init__(model)
        self.agent_class = agent_class
        self.location_class = location_class

    def step(self):
        """ Executes all the stages for all agents. """
        household_keys = [a.unique_id for a in self.agents if isinstance(a, self.agent_class)]
        location_keys = [a.unique_id for a in self.agents if isinstance(a, self.location_class)]

        random.shuffle(household_keys)
        random.shuffle(location_keys)

        for household_key in household_keys:
            self._agents[household_key].step()

        for location_key in location_keys:
            self._agents[location_key].step()

        self.steps += 1
        self.time += 1
