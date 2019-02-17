import twitchbot.api.user


class UserRankModel:
    def __init__(self):
        self.name: str = ''
        self.plural: str = self.name + 's'
        self.power: int = 0

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, UserRankModel) and other.name == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)


class UserRankModelBroadcaster(UserRankModel):
    def __init__(self):
        super().__init__()
        self.name: str = 'broadcaster'
        self.plural: str = self.name
        self.power: int = 100


class UserRankModelVIP(UserRankModel):
    def __init__(self):
        super().__init__()
        self.name: str = 'vip'
        self.power: int = 20


class UserRankModelModerator(UserRankModel):
    def __init__(self):
        super().__init__()
        self.name: str = 'moderator'
        self.power: int = 80


class UserRankModelStaff(UserRankModel):
    def __init__(self):
        super().__init__()
        self.name: str = 'staff'
        self.plural: str = self.name
        self.power: int = 20


class UserRankModelAdmin(UserRankModel):
    def __init__(self):
        super().__init__()
        self.name: str = 'admin'
        self.power: int = 20


class UserRankModelGlobalMod(UserRankModel):
    def __init__(self):
        super().__init__()
        self.name: str = 'global_mod'
        self.power: int = 20


class UserRankModelViewer(UserRankModel):
    def __init__(self):
        super().__init__()
        self.name: str = 'viewer'
        self.power: int = 0


class UserRank:
    BROADCASTER = UserRankModelBroadcaster()
    VIP = UserRankModelVIP()
    MODERATOR = UserRankModelModerator()
    STAFF = UserRankModelStaff()
    ADMIN = UserRankModelAdmin()
    GLOBAL_MOD = UserRankModelGlobalMod()
    VIEWER = UserRankModelViewer()


class UserRankHandler:
    def __init__(self):
        self.ranks: list = []

    def has(self, rank):
        rank = self.convert_rank(rank)
        if rank:
            if rank in self.ranks:
                return True

        return False

    def has_power(self, power: int):
        for rank in self.ranks:
            if rank.power >= power:
                return True
        return False

    def add(self, rank):
        rank = self.convert_rank(rank)
        if rank:
            self.ranks.append(rank)

    def remove(self, rank):
        rank = self.convert_rank(rank)
        if rank:
            self.ranks.remove(rank)

    @staticmethod
    def convert_rank(rank: str):
        if isinstance(rank, str):
            if rank == 'broadcaster':
                return UserRank.BROADCASTER
            elif rank == 'vip' or rank == 'vips':
                return UserRank.VIP
            elif rank == 'moderator' or rank == 'moderators':
                return UserRank.MODERATOR
            elif rank == 'staff':
                return UserRank.STAFF
            elif rank == 'admin' or rank == 'admins':
                return UserRank.ADMIN
            elif rank == 'global_mod' or rank == 'global_mods':
                return UserRank.GLOBAL_MOD
            elif rank == 'viewer' or rank == 'viewers':
                return UserRank.VIEWER
        elif isinstance(rank, UserRankModel):
            return rank

        return False


class User:
    def __init__(self, bot, user, api_user: twitchbot.api.user.User = None):
        self._bot = bot
        self._user = user
        if api_user:
            self.set_user(api_user)

        self.rank: UserRankHandler = UserRankHandler()

    async def init(self):
        self.set_user(await self._bot.api.user(self._user))
        if not isinstance(self, twitchbot.bot.user.Viewer):  # Fix continuous loop. Only set rank when no user is set
            await self.set_ranks()

    def __getattr__(self, item):
        if hasattr(self._user, item):
            return getattr(self._user, item)

        raise AttributeError(f'Attribute {item} does not exist')

    def set_user(self, user: twitchbot.api.user.User):
        self._user = user

    async def set_ranks(self):
        viewer = await self._bot.viewer(str(self._user))
        if isinstance(viewer, User):
            self.rank = viewer.rank

    def is_api(self):
        return isinstance(self._user, twitchbot.api.user.User)

    def __str__(self):
        if isinstance(self._user, twitchbot.api.user.User):
            return str(self._user)
        return str(self._user)

    def __int__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, User) and other.id == self.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)


class Viewer(User):
    pass
