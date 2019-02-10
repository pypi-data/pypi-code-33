from typing import Callable

class LibLoadStatus:
    '''
    Status of a libload operation.
    '''
    finished: bool
    progress: float
    libraryName: str
    timeTaken: float

    def __init__(self):
        self.onFinish: Callable[['LibLoadStatus'], None] = lambda status: None
