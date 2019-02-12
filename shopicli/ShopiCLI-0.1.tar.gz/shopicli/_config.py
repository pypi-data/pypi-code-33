import json
import os
import warnings


class ConfigManager:
    def __init__(self, config_home):
        self.config_home = config_home
        if not os.path.exists(self.config_home):
            os.makedirs(self.config_home, exist_ok=True)

    def load_connections(self):
        return self._load_json('connections')

    def save_connections(self, data):
        return self._save_json('connections', data)

    def create_connection(self, name, config):
        data = self.load_connections()
        if name in data:
            raise ValueError(
                'Connection {} exists! Not overwriting.'
                .format(name))
        data[name] = config
        self.save_connections(data)

    def get_connection(self, name):
        data = self.load_connections()
        return data[name]

    def update_connection(self, name, config):
        data = self.load_connections()
        if name not in data:
            warnings.warn(
                'Connection does not exist: {}. Creating a new one.'
                .format(name))
        data[name] = config
        self.save_connections(data)

    def delete_connection(self, name):
        data = self.load_connections()
        data.pop(name, None)
        self.save_connections(data)

    def _load_json(self, name):
        filename = self._get_json_file_name(name)
        try:
            with open(filename, 'r') as fp:
                return json.load(fp)
        except FileNotFoundError:
            return {}

    def _save_json(self, name, data):
        filename = self._get_json_file_name(name)
        with open(filename, 'w') as fp:
            json.dump(data, fp)
        # TODO: only set file mode on creation?
        os.chmod(filename, mode=0o600)

    def _get_json_file_name(self, name):
        return os.path.join(self.config_home, '{}.json'.format(name))
