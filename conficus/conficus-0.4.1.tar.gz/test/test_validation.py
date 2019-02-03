import conficus
from copy import copy
from datetime import datetime


def test_copy(cfg_pth):
    for name, path in cfg_pth.items():
        config = conficus.load(str(path), inheritance=True)

        # test copy function
        copy_of_config = copy(config)
        assert copy_of_config == config

        # test dict.copy method
        copy_of_config = config.copy()
        assert copy_of_config == config
