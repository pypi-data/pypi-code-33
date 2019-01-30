from cytoolz.curried import curry, assoc
from cytoolz import reduceby

from genomoncology.parse import DocType, __TYPE__, __CHILD__
from .base import LazyFileSource
from .delimited import do_split


@curry
class AggregatedFileSource(LazyFileSource):
    def __init__(self, filename, aggregate_key, delimiter="\t", **meta):
        self.delimiter = delimiter
        self.aggregate_key = aggregate_key
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.AGGREGATE.value)

        super().__init__(filename)

    def __iter__(self):
        # noinspection PyUnresolvedReferences
        iterator = super(AggregatedFileSource.func, self).__iter__()

        self.columns = next(iterator).strip().split(self.delimiter)

        yield self.create_header()

        aggregated_d = reduceby(
            self.get_key_value, self.get_aggregate_value, iterator, dict
        )

        for key, value in aggregated_d.items():
            value["gene"] = key
            value["__type__"] = DocType.AGGREGATE.value
            yield value

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "columns": self.columns,
            "meta": self.meta,
            "file_path": self.name,
        }

    def get_key_value(self, x):
        key = do_split(self.delimiter, x.replace("\n", ""))[
            self.columns.index(self.aggregate_key)
        ]
        return key

    def get_aggregate_value(self, acc, x):
        hold_d = acc
        value_l = do_split(self.delimiter, x.replace("\n", ""))
        for i in range(len(value_l)):
            value = value_l[i] if value_l[i] != "" else "None"
            if self.columns[i] in hold_d:
                hold_d[self.columns[i]] = hold_d[self.columns[i]] + [value]
            else:
                hold_d[self.columns[i]] = [value]
        return hold_d
