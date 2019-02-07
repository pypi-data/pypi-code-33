class Layer:
    """
    Store every parameter concerning a level.
    """
    def __init__(self, volume, layer_name):
        self.layer_name = layer_name
        self.volume = volume

        self.q_in = None  # Inlet flows corresponding to inlet ports
        self.temp_in = None  # Temperatures of inlet flows corresponding to inlet ports
        self.q_out = None  # Outlet flows corresponding to outlet ports
        self.q_top = None  # Flows circulating through the top of a layer
        self.q_bot = None  # Flows circulating through the bottom of a layer
