# All files are expected to receive a set of users.
from six import StringIO
import csv
from terminaltables import AsciiTable

def table_output(users):
    """Return an ASCII table representation of the data."""

    data = [["Student ID", "Name", "Login ID"]]

    for user in users:
        data.append([user.gtID, user.name, user.login])

    table = AsciiTable(table_data)

    return table.table

def json_output(users):
    """Return a JSON list representation of the data"""

    data = [{'gtID': user.gtID, 'name': user.name, 'login':user.login}
        for user in users]

    return json.dumps(data, sort_keys=True, indent=4)

def json_dict_output(users):
    """Return a JSON dictionary representation of the data"""

    d = {user.gtID: {'gtID': user.gtID, 'name': user.name, 'login':user.login}
        for user in users}

    return json.dumps(d, sort_keys=True, indent=4)

def csv_output(users):
    """Return a CSV list of representation of the data"""

    result = ""

    with StringIO() as s:
        fieldnames = ['gtID', 'name', 'login']
        writer = csv.DictWriter(s, fieldnames=fieldnames)

        writer.writerows(users)

        result = s.getvalue()

    return result
