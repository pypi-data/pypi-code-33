from bzflag.networking.game_data import GameData


class BZDBSetting(GameData):
    __slots__ = (
        'name',
        'value',
    )

    def __init__(self):
        super().__init__()

        self.name: str = ''
        self.value: str = ''
