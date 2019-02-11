class IdNameSlug():
    def __init__(self, id_, name, slug):
        self.id = id_
        self.name = name
        self.slug = slug

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.slug


class SimplePlatform(IdNameSlug):
    def __init__(self, id_, name, slug):
        super().__init__(id_, name, slug)


class SimpleStore(IdNameSlug):
    def __init__(self, id_, name, slug):
        super().__init__(id_, name, slug)


class Developer(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Category(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Genre(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Tag(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        super().__init__(id_, name, slug)
        self.games_count = games_count


class Publisher(IdNameSlug):
    def __init__(self, id_, name, slug, games_count):
        super().__init__(id_, name, slug)
        self.games_count = games_count


class ESRB(IdNameSlug):
    def __init__(self, id_, name, slug):
        super().__init__(id_, name, slug)
