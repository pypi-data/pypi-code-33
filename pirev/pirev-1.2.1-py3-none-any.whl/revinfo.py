from .oldrev import oldrev
from .newrev import newrev

def getRevInfo(code):
  return newrev(code) or oldrev(code)
