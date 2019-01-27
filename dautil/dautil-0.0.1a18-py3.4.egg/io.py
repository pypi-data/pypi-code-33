import json
import os


FJSON = 'dautil.json'


def file_exists(tocheck):
    return os.path.isfile(tocheck)


def read_rc():
    old = None

    if file_exists(FJSON):
        with open(FJSON) as f:
            old = json.load(f)

    return old


def update_rc(key, updates):
    rc = {key: updates}
    old = read_rc()

    if old:
        old.update(rc)
        rc = old

    with open(FJSON, 'w') as f:
        json.dump(rc, f, indent=4, sort_keys=True)
