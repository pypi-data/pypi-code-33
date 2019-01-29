from bzflag.networking.game_data import GameData
from bzflag.networking.network_protocol import Vector3F


class FlagData(GameData):
    __slots__ = (
        'index',
        'abbv',
        'status',
        'endurance',
        'owner',
        'position',
        'launch_pos',
        'landing_pos',
        'flight_time',
        'flight_end',
        'initial_velocity',
    )

    def __init__(self):
        super().__init__()

        self.index: int = -1
        self.abbv: str = ''
        self.status: int = -1
        self.endurance: int = -1
        self.owner: int = -1
        self.position: Vector3F = (0.0, 0.0, 0.0)
        self.launch_pos: Vector3F = (0.0, 0.0, 0.0)
        self.landing_pos: Vector3F = (0.0, 0.0, 0.0)
        self.flight_time: float = 0.0
        self.flight_end: float = 0.0
        self.initial_velocity: float = 0.0
