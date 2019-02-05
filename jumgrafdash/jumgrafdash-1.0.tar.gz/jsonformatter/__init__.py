import json


class Jsonformatter:

    file = None
    json_data = None

    def __init__(self, json_file):

        self.file = json_file

    def format_input_json(self, measurement, alias, title):

        with open(self.file, "r") as input_file:
            self.json_data = json.loads(input_file.read())
            self.json_data['panels'][1]['targets'][0]['measurement'] = measurement
            self.json_data['panels'][1]['targets'][0]['alias'] = alias
            self.json_data['panels'][1]['title'] = title
