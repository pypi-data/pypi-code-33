from bzflag.networking.game_data import GameData


class PlayerScore(GameData):
    __slots__ = (
        'wins',
        'losses',
        'team_kills',
    )

    def __init__(self):
        self.wins: int = 0
        self.losses: int = 0
        self.team_kills: int = 0
