def output(dics):
    from awssearch.cli.cli import output_format
    if output_format == "json":
        return json(dics)
    if output_format == "csv":
        return csv(dics)


def csv(dics, keys=None):
    """
    Create a CSV from a dictionary list
    :param dics: dictionary list
    :param keys: Optional, subset of keys. Default is all keys.
    :return: None
    """
    if isinstance(dics, dict):
        dics = [dics]

    if not keys:
        keys = sorted(set().union(*(d.keys() for d in dics)))

    import csv
    import io
    output = io.StringIO()

    dict_writer = csv.DictWriter(output, keys)
    dict_writer.writeheader()
    dict_writer.writerows(dics)
    contents = output.getvalue()

    print(contents)


def default(o):
    import datetime
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def json(dics):
    import json
    print(json.dumps(
        dics,
        sort_keys=True,
        indent=2,
        default=default,
    ))






