from pydnameth.infrastucture.path import get_data_base_path
from pydnameth.config.common import CommonTypes
import os.path
import pickle


def load_excluded(config):
    exclude = []

    if config.annotations.exclude != CommonTypes.none.value:
        fn = get_data_base_path(config) + '/' + config.annotations.exclude
        fn_txt = fn + '.txt'
        fn_pkl = fn + '.pkl'

        if os.path.isfile(fn_pkl):

            f = open(fn_pkl, 'rb')
            exclude = pickle.load(f)
            f.close()

        else:
            f = open(fn_txt)
            exclude = f.readlines()
            exclude = [x.rstrip() for x in exclude]
            f.close()

            f = open(fn_pkl, 'wb')
            pickle.dump(exclude, f, pickle.HIGHEST_PROTOCOL)
            f.close()

    return exclude
