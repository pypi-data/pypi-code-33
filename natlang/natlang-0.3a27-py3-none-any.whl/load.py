import natlang as nl


def __call__(filePattern,
             format='txt', linesToLoad=sys.maxsize, verbose=True, option=None):
    loader = nl.loader.DataLoader(format)
    return loader.load(filePattern,
                       linesToLoad=linesToLoad,
                       verbose=verbose,
                       option=option)
