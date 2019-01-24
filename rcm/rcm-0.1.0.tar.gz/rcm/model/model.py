import logging
import types
import functools

from mesa import Model
from mesa.time import BaseScheduler
from mesa_geo import AgentCreator, GeoAgent, GeoSpace

from ..datacollectors import PandasCollector
from ..initialization import BaseInitialization
from .location_agent import LocationAgent
from .location_model import LocationModel

logger = logging.getLogger('rcm.model.ResidentialChoiceModel')

def agent_satisfaction(agent):
    if isinstance(agent, LocationAgent):
        return None
    else:
        return agent.satisfaction


def number_agents(agent):
    if isinstance(agent, LocationAgent):
        return agent.inhabitants
    else:
        return None


def number_locations(model):
    return len(model.locations)


class ResidentialChoiceModel(Model):
    """The Residential choice model

    Initializing this model requires
     1) A geojson file defining locations where agents can live
     2) The number of migrating agents
     3) A Initialization class for agent initialization
     4) A DiscreteChoice class that implements an agents discrete choice for
        residence
    """
    def __init__(self,
                 locations,
                 N,
                 activation_class,
                 initialization,
                 activation_args=dict(),
                 location_class=LocationAgent,
                 location_agent_args=dict(),
                 schedule_location_agents=False,
                 location_model=None,
                 seed=None):
        if initialization is None:
            raise Exception("Initialization cannot be None")
        elif not isinstance(initialization, BaseInitialization):
            raise Exception("Initialization needs to be an instance of (a subclass of) BaseInitialization")

        if activation_class is None:
            raise Exception("activation_class cannot be None")
        elif not issubclass(activation_class, BaseScheduler):
            raise Exception("activation_class needs to be a (subclass of) BaseScheduler")

        if location_class is None:
            raise Exception("location_class cannot be None")
        elif not issubclass(location_class, GeoAgent):
            raise Exception("location_class needs to be a (subclass of) GeoAgent")

        super().__init__(seed)

        self.running = True
        self.num_agents = N
        self.schedule = activation_class(self, **activation_args)
        self.schedule_location_agents = schedule_location_agents

        self.grid = GeoSpace(crs={"init": "epsg:4326"})

        self.location_class = location_class
        self.location_agent_args = dict(location_agent_args)

        if location_model is not None:
            if not issubclass(location_model, LocationModel):
                raise Exception("location_model needs to be a (subclass of) LocationModel")
            if not callable(getattr(location_model, "step")):
                raise Exception("location_model needs to implement the step function")

            self.location_model = location_model(self)

        location_agent_args['model'] = self

        if isinstance(locations, str):
            AC = AgentCreator(agent_class=location_class, agent_kwargs=location_agent_args)
            agents = AC.from_GeoJSON(GeoJSON=locations, unique_id="Name")

            self.grid.add_agents(agents)
        elif isinstance(locations, functools.partial):
            gen = locations(self.grid)
            self.grid.add_agents([
                self.location_class('Location: ' + str(self.next_id()),
                self, polygon,
                **self.location_agent_args) for polygon in gen])
        elif isinstance(locations, types.GeneratorType):
            self.grid.add_agents([
                self.location_class('Location: ' + str(self.next_id()),
                self, polygon,
                **self.location_agent_args) for polygon in locations])
    
        self.locations = list(self.grid.agents)

        # Workaround for https://github.com/Corvince/mesa-geo/issues/14
        for index_id, agent in enumerate(self.grid.agents):
            agent.idx_id = index_id

        self.datacollector = PandasCollector(
            agent_reporters={
                "Satisfaction": agent_satisfaction,
                "Inhabitants": number_agents
            },
            model_reporters={
                "Locations": number_locations
            },
            tables={
                "LocationCreation": {
                    "columns": ["unique_id", "creation", "removal"],
                    "index": ["unique_id"]
                }
            }
        )

        self.initialize(initialization)
        if self.location_model is not None:
            self.location_model.initialize()

        self.grid.update_bbox()
        logger.info("Initialization Complete")

    def initialize(self, initialization):
        for i in range(self.num_agents):
            agent = initialization.next('Household ' + str(self.next_id()), self)

            self.schedule.add(agent)
            self.grid.add_agents(agent)
            # Workaround for https://github.com/Corvince/mesa-geo/issues/14
            agent.idx_id = self.grid.idx.maxid

        if self.schedule_location_agents:
            for i in range(len(self.locations)):
                self.schedule.add(self.locations[i])
                self.datacollector.add_table_row("LocationCreation", {
                        "unique_id": self.locations[i].unique_id,
                        "creation": self.schedule.time
                    }, columns=["unique_id", "creation"])

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if self.location_model is not None:
            self.location_model.step()
    
    def reregister(self, agent):
        self.grid.remove_agent(agent)
        self.grid.add_agents(agent)
        # Workaround for https://github.com/Corvince/mesa-geo/issues/14
        agent.idx_id = self.grid.idx.maxid

    def add_location(self, agent):
        self.grid.add_agents(agent)
        # Workaround for https://github.com/Corvince/mesa-geo/issues/14
        agent.idx_id = self.grid.idx.maxid
        self.locations.append(agent)
        if self.schedule_location_agents:
            self.schedule.add(agent)
            self.datacollector.add_table_row("LocationCreation", {
                    "unique_id": agent.unique_id,
                    "creation": self.schedule.time
                }, columns=["unique_id", "creation"])

    def remove_location(self, agent):
        print("Removing location: ", agent.unique_id)
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)
        self.locations.remove(agent)
        self.update_location_removal(agent)

    def update_location_removal(self, location):
        self.datacollector.update_table_row("LocationCreation", location.unique_id, {
            'removal': self.schedule.time
        }, columns=['removal'])
