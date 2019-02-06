from clav.data import ottr
from clav.data.format.base import Format
from clav.os import dump

class Msgpack(Format):

  def __init__(self):
    super().__init__()
