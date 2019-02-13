class TagBulkResponse:

    def __init__(self, count, total, offset, results):
        self.count = count
        self.total = total
        self.offset = offset
        self.results = results
