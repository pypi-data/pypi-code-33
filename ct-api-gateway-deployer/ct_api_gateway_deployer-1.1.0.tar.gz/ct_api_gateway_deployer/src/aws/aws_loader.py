# -*- coding: utf-8 -*-
import json


class AWSLoader:
    def __init__(self, file_path):
        self._aws_config_file = dict()
        self.load_json_config(file_path)

    def load_json_config(self, file_path):
        try:
            with open(file_path) as f:
                data = json.load(f)  # type: object
        except Exception as exp:
            print('Error trying to load the config file')
            raise exp
        self._aws_config_file = data

    def print_config(self):
        print(self._aws_config_file)

    def get_info_title(self):
        return self._aws_config_file['apiGateway']['name']

    def get_servers_url(self):
        return self._aws_config_file['apiGateway']['baseEndpointURL']

    def get_servers_url_variables_base_path_default(self):
        return self._aws_config_file['apiGateway']['basePath']

    def get_rest_api_id(self):
        return self._aws_config_file['apiGateway']['rest_api_id']

    def get_stage_name(self):
        return self._aws_config_file['apiGateway']['stage']
