# -*- coding: utf-8 -*-

from datetime import date, datetime


class ModelClass:

    @staticmethod
    def _parse(cls, row):

        def _convert(value, new_type):
            # TODO : Adjust for convert date and datetime
            if isinstance(new_type, date):
                return value
            if isinstance(new_type, datetime):
                return value
            else:
                return new_type(value)

        return cls._make([
            _convert(
                value,
                cls._field_types.get(cls._fields[index], str)
            )
            for index, value in enumerate(row)
        ])
