#!/usr/bin/env python

import logging
import re

class Misc(object):
  _handler = logging.StreamHandler()

  def __init__(self):
    self._handler.setLevel(logging.DEBUG)
    self._handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))

  def getLogger(self, name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(self._handler)
    return logger

  def labelify(self, label):
    if type(label) == str:
      return re.sub('\W{1,}', '_', label).upper()
    return label

  def stringToArray(self, labels):
    if isinstance(labels, str):
      return filter(lambda s: len(s) > 0, map(lambda s: s.strip(), re.split(r',', labels)))
    return []

misc = Misc()
