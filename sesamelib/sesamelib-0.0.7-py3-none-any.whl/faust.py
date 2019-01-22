import faust


class BaseDynamicMessage(faust.Record):
    x: float
    y: float
    mmsi: str
    tagblock_timestamp: int
    true_heading: float
    sog: float


class MutatedDynamicMessage(BaseDynamicMessage):
    ## 1000 * tagblock_timestamp
    timestamp: float= None
    ## human timestamp
    human_timestamp: str = None
    ## grid_x, grid_y: lower_left point on the grid
    grid_x: float = None
    grid_y: float = None
    ## (x-px)
    d0x: float = None
    ## (y-py)
    d0y: float = None
    ## (t - pt)
    d0t: float = None
    ## closest zone
    zone_mrgid: str = None
    zone_distance: float = None

    @classmethod
    def fromBasicMessage(cls, msg):
        return cls(x=msg.x,
                   y=msg.y,
                   mmsi=msg.mmsi,
                   tagblock_timestamp=msg.tagblock_timestamp,
                   timestamp=msg.timestamp,
                   true_heading=msg.true_heading,
                   sog=msg.sog)
