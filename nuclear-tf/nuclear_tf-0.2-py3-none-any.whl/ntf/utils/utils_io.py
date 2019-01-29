import _pickle as p
import json
import yaml


def load_binary(path):
    with open(path, 'rb') as f:
        return p.load(f)


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.load(f)


def load_txt(path):
    with open(path, 'r') as f:
        return f.read()


def save_binary(d, path):
    with open(path, 'wb') as f:
        p.dump(d, f)


def save_json(d, path):
    with open(path, 'w') as f:
        json.dump(d, f, indent=4)


def save_yaml(d, path):
    with open(path, 'w') as f:
        yaml.dump(d, f)


def save_txt(s, path):
    with open(path, 'w') as f:
        return f.write(s)
