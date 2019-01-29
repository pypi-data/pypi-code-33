from bzflag.networking.game_data import GameData


class ScoreData(GameData):
    __slots__ = (
        'player_id',
        'wins',
        'losses',
        'team_kills',
    )

    def __init__(self):
        super().__init__()

        self.player_id: int = -1
        self.wins: int = 0
        self.losses: int = 0
        self.team_kills: int = 0
