#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  item.py
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements the Item object that is used by the entire suite 
#

import uuid

from ditto_lib.generic.config import logger

class Item:

    def __init__(self, name, attributes={}):
        self.__id = uuid.uuid4()
        self.__hash = hash(name)
        self._name = name
        self._attributes = attributes

    def __hash__(self):
        return self.__hash

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __repr__(self):
        return "Item name {}".format(self.name)

    def size(self):
        '''
        Returns how many attributes pertain to this item
        '''
        return len(self.attributes)

    @property
    def name(self):
        '''
        Name of the item
        '''
        return self._name

    @name.setter
    def name(self, name):
        logger.log('debug', "{} name set to {}".format(self._name, name))
        self._name = name

    @property
    def attributes(self):
        '''
        Mapping of attribute name --> attribute class.
        Value will be None if not yet set
        '''
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = attributes

    def get_attribute(self, name):
        if name not in self._attributes:
            logger.log('error', "Could not get attribute {} from {}".format(name, self.name))
            return None
        else:
            return self._attributes[name]

    def get_attributes(self, attribute_names):
        '''
        Return list of attribute with given names
        '''
        attributes = []
        for name in attribute_names:
            current_attribute = self.get_attribute(name)
            if current_attribute:
                attributes.append(current_attribute)
        return attributes

    def contains(self, attribute_name):
        '''
        Returns whether the item contains 
        the attribute given
        '''
        return attribute_name in self.attributes

    @property
    def id(self):
        '''
        Return the uuid of this item
        '''
        return self.__id

    def add_attribute(self, attribute):
        self._attributes[attribute.name] = attribute
        logger.log('debug', "Attribute {} with value {} added to Item {}".format(attribute.name, attribute.value, self.name))
    
    def remove_attribute(self, attribute):
        if attribute not in self.attributes:
            logger.log('error', "Could not remove {} because it doesn't exist in {}".format(attribute, self.name))
        else:
            del self.attributes[attribute]
    
    def copy(self):
        '''
        Return a deep copy of this item
        '''
        item = Item(self.name)
        for attribute in self.attributes.values():
            copy = attribute.copy()
            item.attributes[copy.name] = copy
        return item