from torch.utils import data


class DataLoader(data.DataLoader):
    """
    serializable dataloader
    """
    def __init__(self, dataset, **kwargs):
        super(DataLoader, self).__init__(dataset, **kwargs)
        self.kwargs = kwargs
        self.dataset = dataset

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
