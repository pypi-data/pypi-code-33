import csv
import json


def reader(*a, **k):
    for row in csv.reader(*a, **k):
        parsed_row = []
        for column in row:
            try:
                parsed_row.append(json.loads(column))
            except:
                parsed_row.append(column)
        yield parsed_row
