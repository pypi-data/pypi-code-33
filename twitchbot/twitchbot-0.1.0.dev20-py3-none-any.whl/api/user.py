

class User:
    def __init__(self, api, data):
        self._api = api
        self.id: int = int(data.get('id', None))
        self.login: str = str(data.get('login', None))
        self.display_name: str = str(data.get('display_name', self.login))
        self.mention: str = '@' + self.display_name
        self.type: str = str(data.get('type', None))
        self.broadcaster_type: str = str(data.get('broadcaster_type', None))
        self.description: str = str(data.get('description', None))
        self.view_count: int = int(data.get('view_count', 0))

    async def follows(self, user: 'User'):
        return await self._api.follows(self, user)

    def __str__(self):
        return self.login
