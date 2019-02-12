from .. import const, errors
from ..output_processor import dict, translate, img
import random


def _link_to_random_output_processor(emo, n):
    if n == 0:
        return dict.get_output(emo)
    elif n == 1:
        return img.get_output(emo)
    else:
        raise errors.OUT_OF_OUTPUT_COUNT_BOUNDARY_ERROR()


def _link_to_output_processor(arg):
    emo = arg.emotion
    if arg.dict:
        return dict.get_output(emo)
    elif arg.translate:
        return dict.get_output(translate.get_output(emo))
    elif arg.img:
        return img.get_output(emo)
    else:
        return _link_to_random_output_processor(emo, random.randrange(0,
                                                const.OUTPUT_COUNT))


def get_output(arg):
    return _link_to_output_processor(arg)
