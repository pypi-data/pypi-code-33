#!/usr/bin/env python

import os
import semver
from misc import misc

DEFAULT_NAMESPACE = "CODETAGS"

class Codetags(object):
  def __init__(self, **kwargs):
    self.__store = { "env": {}, "cachedTags": {}, "declaredTags": [] }
    self.__presets = {}
    self.initialize(**kwargs)
    pass

  def initialize(self, **kwargs):
    for field_name in ["namespace", "includedTagsLabel", "excludedTagsLabel"]:
      if field_name in kwargs and type(kwargs[field_name]) == str:
        self.__presets[field_name] = misc.labelify(kwargs[field_name])
    for field_name in ["version"]:
      if field_name in kwargs and type(kwargs[field_name]) == str:
        self.__presets[field_name] = kwargs[field_name]
    return self

  def register(self, descriptors):
    if isinstance(descriptors, list):
      # filter valid descriptors
      def descriptors_filter_handler(descriptor):
        if isinstance(descriptor, str):
          return True
        if isinstance(descriptor, dict) and "name" in descriptor:
          if "plan" in descriptor:
            plan = descriptor["plan"]
            if isinstance(plan, dict) and "enabled" in plan and isinstance(plan["enabled"], bool):
              if "version" in self.__presets and self._isVersionValid(self.__presets["version"]):
                _validated = True
                _satisfied = True
                if "minBound" in plan and isinstance(plan["minBound"], str):
                  _validated = _validated and self._isVersionValid(plan["minBound"])
                  if _validated:
                    _satisfied = _satisfied and self._isVersionLTE(plan["minBound"], self.__presets["version"])
                    pass
                  pass
                if "maxBound" in plan and isinstance(plan["maxBound"], str):
                  _validated = _validated and self._isVersionValid(plan["maxBound"])
                  if _validated:
                    _satisfied = _satisfied and self._isVersionLT(self.__presets["version"], plan["maxBound"])
                    pass
                  pass
                if _validated:
                  if _satisfied:
                    return plan["enabled"]
                  else:
                    if "enabled" in descriptor and isinstance(descriptor["enabled"], bool):
                      return descriptor["enabled"]
                    return not plan["enabled"]
                  pass
          # determine enabled value
          if "enabled" in descriptor and isinstance(descriptor["enabled"], bool):
            return descriptor["enabled"]
          # return default value
          return True
        # not (string and dict)
        return False
      refs = filter(descriptors_filter_handler, descriptors)
      # extract tag labels
      def descriptors_map_handler(descriptor):
        if isinstance(descriptor, str):
          return descriptor
        if isinstance(descriptor, dict) and "name" in descriptor:
          return descriptor["name"]
        return None
      tags = map(descriptors_map_handler, refs)
      # add to declaredTags
      for tag in tags:
        if not tag in self.__store["declaredTags"]:
          self.__store["declaredTags"].append(tag)
    return self

  def isActive(self, *tagexps):
    return self._isArgumentsSatisfied(tagexps)
  
  def clearCache(self):
    self.__store["cachedTags"].clear()
    self._refreshEnv()
    return self
  
  def reset(self):
    self.clearCache()
    del self.__store["declaredTags"][:]
    self.__presets.clear()
    return self

  def _refreshEnv(self):
    self.__store["env"].clear()
    for tagType in ["includedTags", "excludedTags"]:
      self.__store[tagType] = self._getEnv(self._getLabel(tagType))
    return self
  
  def _getLabel(self, tagType):
    _label = '_'
    if "namespace" in self.__presets and isinstance(self.__presets["namespace"], str):
      _label = self.__presets["namespace"] + _label
    else:
      _label = DEFAULT_NAMESPACE + _label
    if tagType == "includedTags":
      return _label + ("INCLUDED_TAGS" if not "includedTagsLabel" in self.__presets else self.__presets["includedTagsLabel"])
    if tagType == "excludedTags":
      return _label + ("EXCLUDED_TAGS" if not "excludedTagsLabel" in self.__presets else self.__presets["excludedTagsLabel"])
    return _label + (misc.labelify(tagType) if not tagType in self.__presets else self.__presets[tagType])

  def _getEnv(self, label, defaultValue = None):
    # label is not a string
    if not isinstance(label, str):
      return None
    # environment variable has been cached
    if label in self.__store["env"]:
      return self.__store["env"][label]
    # determine environment value
    self.__store["env"][label] = None
    if isinstance(defaultValue, str):
      self.__store["env"][label] = defaultValue
    environValue = os.environ.get(label)
    if isinstance(environValue, str):
      self.__store["env"][label] = environValue
    # convert string to list
    self.__store["env"][label] = misc.stringToArray(self.__store["env"][label])
    return self.__store["env"][label]

  def getDeclaredTags(self):
    return self._cloneTags("declaredTags")

  def getExcludedTags(self):
    return self._cloneTags("excludedTags")

  def getIncludedTags(self):
    return self._cloneTags("includedTags")

  def _cloneTags(self, tagType):
    if tagType in self.__store:
      return self.__store[tagType][0::]
    return []

  def _isArgumentsSatisfied(self, arguments):
    for arg in arguments:
      if self._evaluateExpression(arg):
        return True
    return False

  def _isAllOfLabelsSatisfied(self, exps):
    if isinstance(exps, list):
      for exp in exps:
        if not self._evaluateExpression(exp):
          return False
      return True
    return self._evaluateExpression(exps)
  
  def _isAnyOfLabelsSatisfied(self, exps):
    if isinstance(exps, list):
      for exp in exps:
        if self._evaluateExpression(exp):
          return True
      return False
    return self._evaluateExpression(exps)

  def _isNotOfLabelsSatisfied(self, exp):
    return not self._evaluateExpression(exp)

  def _evaluateExpression(self, exp):
    if isinstance(exp, dict):
      for op, subexp in exp.items():
        if op == '$not':
          if self._isNotOfLabelsSatisfied(subexp) == False:
            return False
        elif op == '$any':
          if self._isAnyOfLabelsSatisfied(subexp) == False:
            return False
        elif op == '$all':
          if self._isAllOfLabelsSatisfied(subexp) == False:
            return False
        else:
          return False
      return True
    elif isinstance(exp, list):
      return self._isAllOfLabelsSatisfied(exp)
    return self._checkLabelActivated(exp)

  def _checkLabelActivated(self, label):
    if isinstance(label, str):
      if label in self.__store["cachedTags"]:
        return self.__store["cachedTags"][label]
      self.__store["cachedTags"][label] = self._forceCheckLabelActivated(label)
      return self.__store["cachedTags"][label]
    return False
  
  def _forceCheckLabelActivated(self, label):
    if label in self.__store["excludedTags"]:
      return False
    if label in self.__store["includedTags"]:
      return True
    return label in self.__store["declaredTags"]
  
  def _isVersionValid(self, version):
    try:
      versionInfo = semver.parse(version)
      return True
    except:
      return False

  def _isVersionLTE(self, version1, version2):
    return semver.compare(version1, version2) <= 0
  
  def _isVersionLT(self, version1, version2):
    return semver.compare(version1, version2) < 0

INSTANCES = {}

def _validateInstanceName(name):
  if not isinstance(name, str):
    raise TypeError("The name of a codetags instance must be a string")
  pass

def newInstance(name, **kwargs):
  name = misc.labelify(name)
  _validateInstanceName(name)
  if name == DEFAULT_NAMESPACE and name in INSTANCES:
    raise ValueError(DEFAULT_NAMESPACE + " is default instance name. Please provides another name.")
  INSTANCES[name] = Codetags(**kwargs)
  return INSTANCES[name]

def getInstance(name, **kwargs):
  name = misc.labelify(name)
  _validateInstanceName(name)
  if name in INSTANCES and isinstance(INSTANCES[name], Codetags):
    INSTANCES[name].initialize(**kwargs)
    return INSTANCES[name]
  else:
    return newInstance(name, **kwargs)
  pass

default = getInstance(DEFAULT_NAMESPACE)
