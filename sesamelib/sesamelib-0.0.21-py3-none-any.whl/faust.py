import faust


class BaseDynamicMessage(faust.Record):
    x: float
    y: float
    mmsi: str
    tagblock_timestamp: int
    true_heading: float
    sog: float


class MutatedDynamicMessage(BaseDynamicMessage):
    timestamp: float = None
    human_timestamp: str = None
    grid_x: float = None
    grid_y: float = None
    dx: list = None
    dy: list = None
    dt: list = None
    zone_mrgid: str = None
    zone_distance: float = None

    @classmethod
    def fromBasicMessage(cls, msg):
        self = cls(x=msg.x,
                   y=msg.y,
                   mmsi=msg.mmsi,
                   tagblock_timestamp=msg.tagblock_timestamp,
                   true_heading=msg.true_heading,
                   sog=msg.sog)
        self.dx = []
        self.dy = []
        self.dt = []
        return self
