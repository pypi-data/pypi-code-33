from typing import Optional

from bzflag.networking.game_data import GameData
from bzflag.networking.game_data_shot import ShotData


class FiringInfoData(GameData):
    __slots__ = (
        'time_sent',
        'shot',
        'flag',
        'lifetime',
    )

    def __init__(self):
        super().__init__()

        self.time_sent: float = 0.0
        self.shot: Optional[ShotData] = None
        self.flag: str = ''
        self.lifetime: float = 0.0
