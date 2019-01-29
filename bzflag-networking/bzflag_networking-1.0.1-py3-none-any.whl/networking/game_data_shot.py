from bzflag.networking.game_data import GameData
from bzflag.networking.network_protocol import Vector3F


class ShotData(GameData):
    __slots__ = (
        'player_id',
        'shot_id',
        'position',
        'velocity',
        'delta_time',
        'team',
    )

    def __init__(self):
        super().__init__()

        self.player_id: int = -1
        self.shot_id: int = -1
        self.position: Vector3F = (0.0, 0.0, 0.0)
        self.velocity: Vector3F = (0.0, 0.0, 0.0)
        self.delta_time: float = 0.0
        self.team: int = -1
