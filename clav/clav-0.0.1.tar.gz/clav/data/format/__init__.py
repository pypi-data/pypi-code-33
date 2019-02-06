from .json import Json
from .msgpack import Msgpack
from .yaml import Yaml

json = Json()
msgpack = Msgpack()
yaml = Yaml()

from clav.data.attribute import attr

formats = attr(
  jsn = json,
  json = json,
  mpack = msgpack,
  mpck = msgpack,
  mpk = msgpack,
  msgpack = msgpack,
  msgpck = msgpack,
  yaml = yaml,
  yml = yaml,
)

del attr
