from __future__ import absolute_import
import sys
import json
from flatast.json_format import MessageToJson
from flatast.fast_pb2 import Data
if __name__ == "__main__":
    json.dumps([])
    data = Data()
    with open(sys.argv[1], 'rb') as f:
         data.ParseFromString(f.read())
         f.close()
         j = MessageToJson(data)
         print(j)
