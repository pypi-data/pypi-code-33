import sys
from .pirev import getInfo

filename = None
if len(sys.argv) > 1:
  filename = sys.argv[1]

try:
  print(getInfo(filename=filename))
except Exception as error:
  print(error)
