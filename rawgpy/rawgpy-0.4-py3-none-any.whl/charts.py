class Chart():
    def __init__(self, position, change):
        self.position = position
        self.change = change


class GenreChart(Chart):
    def __init__(self, genre, position, change):
        super().__init__(position, change)
        self.genre = genre


class YearChart(Chart):
    def __init__(self, year, position, change):
        super().__init__(position, change)
        self.year = year
