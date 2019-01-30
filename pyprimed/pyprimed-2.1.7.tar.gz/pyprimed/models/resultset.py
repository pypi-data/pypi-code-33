# -*- coding: utf-8 -*-

import re
import json


class RangeParsingFailure(Exception):
    pass


class ResultSet:
    @staticmethod
    def parse_range(range_str):
        match = re.search(r"\w+\s(\d+)\-(\d+)/(\d+)", range_str)
        if match is None:
            raise RangeParsingFailure(
                "Could not parse range from string: {range_str}".format(
                    range_str=range_str
                )
            )
        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def __init__(self, caller, request):
        result_json, range = caller.root._dispatch_request(**request)

        self._caller = caller
        self._request = request
        self._result_json = result_json
        self._range = ResultSet.parse_range(range)

    def __getitem__(self, i):
        if isinstance(i, int):
            if i < 0:
                return self[i + len(self)]

            if i >= len(self):
                return self[i - len(self)]

            if self._page_start <= i and i < self._page_end:
                idx = i - self._page_start
                return self._caller._RESOURCE(
                    parent=self._caller, **self._result_json[idx]
                )
            else:
                page_start = i // self._page_size * self._page_size
                page_end = page_start + self._page_size

                self._request["params"]["range"] = json.dumps([page_start, page_end])
                result_json, _range = self._caller.root._dispatch_request(
                    **self._request
                )

                self._result_json = result_json
                self._range = ResultSet.parse_range(_range)

                return self[i]

        elif isinstance(i, slice):
            return [self[idx] for idx in range(*i.indices(len(self)))]

        else:
            raise TypeError("Invalid argument type.")

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    @property
    def first(self):
        if len(self) > 0:
            return self[0]
        else:
            return None

    def __len__(self):
        return int(self._range[2])

    @property
    def _page_start(self):
        return int(self._range[0])

    @property
    def _page_end(self):
        return int(self._range[1])

    @property
    def _page_size(self):
        return self._page_end - self._page_start
