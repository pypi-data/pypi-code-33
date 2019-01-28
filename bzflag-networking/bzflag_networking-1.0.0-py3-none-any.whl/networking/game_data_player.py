from bzflag.networking.game_data import GameData

IsRegistered = 1 << 0
IsVerified = 1 << 1
IsAdmin = 1 << 2


class PlayerData(GameData):
    __slots__ = (
        'player_id',
        'is_registered',
        'is_verified',
        'is_admin',
    )

    def __init__(self):
        self.player_id = -1
        self.is_registered = False
        self.is_verified = False
        self.is_admin = False
