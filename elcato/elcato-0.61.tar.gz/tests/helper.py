import os
import shutil
from elcato.helpers import load_template, loadconfig


def test_setup(name, config_name):
    source = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(source, "fixtures")
    config = loadconfig(config_path, name=config_name)

    path = f"/tmp/elcato/{name}"
    if os.path.exists(path):
        shutil.rmtree(path)
    return path, config
