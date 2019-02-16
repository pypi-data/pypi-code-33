import pandas as pd

class MongoCursorReader(object):
    def __init__(self, cursor, chunk_size = 10000):
        self._cursor = cursor
        self._chunk_size = chunk_size
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        """Turn an iterator into multiple (small) pandas.DataFrame

        This is a balance between memory and efficiency.
        TODO: Possibly inefficient implementation.
        """
        records = []
        for idx, record in enumerate(self._cursor):
            records.append(record)
            if idx % self._chunk_size == self._chunk_size - 1:
                df = pd.DataFrame(records)
                records = []
                return df
        if records:
            df = pd.DataFrame(records)
            records = []
            return df
        else:
            raise StopIteration

    def next(self):
        return self.__next__()

