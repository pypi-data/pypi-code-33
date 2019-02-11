

class Stream:
    def __init__(self, api, data):
        self._api = api
        self.id: int = int(data.get('id', None))
        self.user_id: int = int(data.get('user_id', None))
        self.user_display_name: str = str(data.get('user_name', None))
        self.user_login = self.user_display_name.lower() if self.user_display_name else None
        self.game_id: int = int(data.get('game_id', None))
        self.live: bool = True if data.get('type', False) else False
        self.title: str = str(data.get('title', None))
        self.started_at: str = str(data.get('started_at', None))
        self.language: str = str(data.get('language', None))
        self.type: str = str(data.get('type', None))
        self.view_count: int = int(data.get('viewer_count', 0))

    def __str__(self):
        return self.user_login
