from .. import errors
from . import dict_processor


def _decide_language(emo):
    if all('a' <= ch <= 'z' for ch in emo):
        return 'eng'
    elif all('가' <= ch <= '힣' for ch in emo):
        return 'kor'
    else:
        raise errors.UNKNOWN_LANG_ERROR()


def _fetch_meaning(emo):
    # Parse HTML of website
    try:
        lang = _decide_language(emo)
        return dict_processor.get_output(emo, lang)
    except errors.UNKNOWN_LANG_ERROR as e:
        print(e)


def get_output(emo):
    return _fetch_meaning(emo)
