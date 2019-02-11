
class Platform():
    def __init__(self, id_, name, slug, image, year_end, year_start, games_count, released_at, minimum_requirements, maximum_requirements):
        self.id_ = id_
        self.name = name
        self.slug = slug
        self.image = image
        self.year_end = year_end
        self.year_start = year_start
        self.games_count = games_count
        self.released_at = released_at
        self.minimum_requirements = minimum_requirements
        self.maximum_requirements = maximum_requirements
