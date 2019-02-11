class Rating():
    def __init__(self, id_, title, count, percent):
        self.id = id_
        self.title = title
        self.count = count
        self.percent = percent

    def __str__(self):
        return "{title} {percent}%".format(title=self.title, percent=self.percent)

    def __repr__(self):
        return "{title} {percent}%".format(title=self.title, percent=self.percent)
