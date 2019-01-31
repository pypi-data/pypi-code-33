from bootstrap.lib.options import Options
from . import CrossEntropyLoss


def factory(engine, mode):
    if Options()['model']['criterion']['name'] == "cross_entropy":
        criterion = CrossEntropyLoss()
    else:
        raise ValueError
    return criterion
