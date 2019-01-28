from bzflag.networking.game_data import GameData


class ScoreData(GameData):
    __slots__ = (
        'player_id',
        'wins',
        'losses',
        'team_kills',
    )
