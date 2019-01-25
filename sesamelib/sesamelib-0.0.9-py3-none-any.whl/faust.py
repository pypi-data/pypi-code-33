import faust


class BaseDynamicMessage(faust.Record):
    x: float
    y: float
    mmsi: str
    tagblock_timestamp: int
    true_heading: float
    sog: float


class MutatedDynamicMessage(BaseDynamicMessage):

    def __init__(self, *,
                 timestamp: float = None,
                 human_timestamp: str = None,
                 grid_x: float = None,
                 grid_y: float = None,
                 dx: list = None,
                 dy: list = None,
                 dt: list = None,
                 zone_mrgid: str = None,
                 zone_distance: float = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.timestamp = timestamp
        self.human_timestamp = human_timestamp
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.dx = dx if dx is not None else []
        self.dy = dy if dy is not None else []
        self.dt = dt if dt is not None else []
        self.zone_mrgid = zone_mrgid
        self.zone_distance = zone_distance


    @classmethod
    def fromBasicMessage(cls, msg):
        return cls(x=msg.x,
                   y=msg.y,
                   mmsi=msg.mmsi,
                   tagblock_timestamp=msg.tagblock_timestamp,
                   true_heading=msg.true_heading,
                   sog=msg.sog)


class Test(faust.Record):
    deq: list = []
