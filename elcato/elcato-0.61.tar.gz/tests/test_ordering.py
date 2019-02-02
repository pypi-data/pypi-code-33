
import os
import sys
import json
import helper
from elcato import settings
from elcato.helpers import load_template, loadconfig
from elcato import build_file, build
from elcato.helpers import handle_config


# TODO take out hard coded posts folder
def test_ordering():
    destination, config = helper.test_setup("ordering/", "elcato-json.yaml")
    source = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(f"{source}/../")

    build(root, destination, config)
    assert settings.TEMPLATE is not None
    index_path = f"{destination}index.json"
    with open(index_path, "r") as fp:
        value = json.loads(fp.read())
        assert value.get("title") == "Index"
        assert len(value.get("cards")) == 4
        dates = [p.get("date") for p in value.get("cards")]

        assert dates == [
            " 2018-10-10 12:00:00 UTC",
            " 2018-10-09 12:00:00 UTC",
            " 2018-10-08 12:00:00 UTC",
            " 2017-07-01 12:00:00 UTC",
        ]
