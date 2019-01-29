from bzflag.networking.game_data import GameData


class TeamData(GameData):
    __slots__ = (
        'team',
        'size',
        'wins',
        'losses',
    )
