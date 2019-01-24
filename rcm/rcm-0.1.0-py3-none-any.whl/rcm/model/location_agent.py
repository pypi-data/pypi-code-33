from mesa_geo import GeoAgent


class LocationAgent(GeoAgent):
    def __init__(self, unique_id, model, shape):
        super().__init__(unique_id, model, shape)
        self.inhabitants = 0
    
    def step(self):
        others = [o for o in self.model.grid.get_relation(self, 'contains') if o.unique_id != self.unique_id and not isinstance(o, LocationAgent)]
        self.inhabitants = len(others)
