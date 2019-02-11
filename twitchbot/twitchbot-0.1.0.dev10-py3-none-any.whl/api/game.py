

class Game:
    def __init__(self, api, data):
        self._api = api
        self.id: int = int(data.get('id', None))
        self.name: str = str(data.get('name', None))
        if self.name:
            self.name = self.name.lower()
        self.display_name: str = str(data.get('name', None))

    def __str__(self):
        return self.name
