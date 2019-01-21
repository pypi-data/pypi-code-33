#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  attribute.py
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements class which describes a DataFrame attribute
#

import copy

class Attribute:

    def __init__(self, name, value=None, is_descriptor=True):
        self._name = name
        self._value = value
        self.__hash = hash(self.name)
        self._is_descriptor = is_descriptor

        if value is not None and is_descriptor is True:
            self._value = float(value)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name \
            and self.is_descriptor == other.is_descriptor and self.value == other.value

    def __hash__(self):
        return self.__hash

    def __str__(self):
        return "Attribute name: {}".format(self.name) + " | Attribute value: {}".format(self.value) + " | Attribute is descriptor: {}".format(self.is_descriptor)

    @property
    def name(self):
        '''
        Name of the frame
        '''
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value is not None:
            self._value = float(value)
        else:
            self._value = value

    @property
    def is_descriptor(self):
        '''
        Returns whether this attribute is a descriptor of 
        whoever is holding it or not
        '''
        return self._is_descriptor

    @is_descriptor.setter
    def is_descriptor(self, is_descriptor):
        self._is_descriptor = is_descriptor

    def copy(self):
        '''
        Return a copy of this attribute.
        '''
        new_attribute = Attribute(self.name)
        new_attribute.is_descriptor = self.is_descriptor
        new_attribute._value = self.value
        return new_attribute