from bzflag.networking.game_data import GameData


class PlayerInfo(GameData):
    __slots__ = (
        'player_index',
        'ip_address',
    )

    def __init__(self):
        super().__init__()

        self.player_index: int = -1
        self.ip_address: str = ''
