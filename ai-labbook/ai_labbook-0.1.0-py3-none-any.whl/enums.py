from enum import Enum

class ExpEvent(Enum):
    START    = 1
    STOP     = 2
    SAVE     = 3
    LOAD     = 4
    EPOCH    = 5
    STEP     = 6
