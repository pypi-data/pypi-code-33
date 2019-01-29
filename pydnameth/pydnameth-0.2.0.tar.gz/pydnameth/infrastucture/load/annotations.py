from pydnameth.infrastucture.path import get_data_base_path
from pydnameth.config.annotations.types import AnnotationKey
import os.path
import pickle


def load_annotations_dict(config):
    fn = get_data_base_path(config) + '/' + config.annotations.name
    fn_txt = fn + '.txt'
    fn_pkl = fn + '.pkl'

    if os.path.isfile(fn_pkl):

        f = open(fn_pkl, 'rb')
        annotations_dict = pickle.load(f)
        f.close()

    else:

        possible_keys = [x.value for x in AnnotationKey]
        f = open(fn_txt)
        key_line = f.readline()
        keys = key_line.split('\t')
        keys = [x.rstrip() for x in keys]

        annotations_dict = {}
        for key in keys:
            if key in possible_keys:
                annotations_dict[key] = []

        for line in f:
            values = line.split('\t')
            for key_id in range(0, len(keys)):
                key = keys[key_id]
                if key in possible_keys:
                    annotations_dict[key].append(values[key_id].rstrip())
        f.close()

        f = open(fn_pkl, 'wb')
        pickle.dump(annotations_dict, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    return annotations_dict
