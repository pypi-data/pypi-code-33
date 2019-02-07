import os
import pickle


class Sorting:

    def __init__(self, *args):
        self.attribute_names = args

    def __call__(self, instance):
        values = []

        for attr in self.attribute_names:
            values.append(getattr(instance, attr))

        return values


def load_rada():
    db_path = os.path.dirname(os.path.abspath(__file__)) + '/db.pickle'
    if not os.path.exists(db_path):
        return None

    with open(db_path, 'rb') as source:
        data = pickle.load(source)
    return data['rada']


def save_rada(rada):
    database_path = os.path.dirname(os.path.abspath(__file__)) + '/db.pickle'

    with open(database_path, 'wb') as target:
        pickle.dump({'rada': rada}, target)
