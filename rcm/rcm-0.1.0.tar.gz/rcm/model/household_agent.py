from mesa_geo import GeoAgent


class HouseholdAgent(GeoAgent):
    def __init__(self, unique_id, model, shape, location):
        super().__init__(unique_id, model, shape)
        self.location = location

    def step(self):
        pass

    def __geo_interface__(self):
        props = super().__geo_interface__()

        # Remove non serializable attributes
        del props['properties']['location']

        return props
