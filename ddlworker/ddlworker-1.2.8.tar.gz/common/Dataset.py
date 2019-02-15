#TODO: remove dataset
class Dataset(object):
    dataset_location = None
    folder_structure = None

    def __init__(self, dataset_location, folder_structure):
        self.dataset_location = dataset_location
        self.folder_structure = folder_structure
