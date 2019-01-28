from bzflag.networking.game_data import GameData


class PlayerInfo(GameData):
    __slots__ = (
        'player_index',
        'ip_address',
    )
