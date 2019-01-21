#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# cluster.py
# Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
# Implements a Cluster object 
#

from ditto_lib.generic.itemcollection import ItemCollection, Item, logger

from ordered_set import OrderedSet

class Cluster():

    def __init__(self, name=None):
        self._name = name
        self._items = []

    def __repr__(self):
        return "Cluster {}".format(self.name)

    def __len__(self):
        '''
        Returns the amount of items in this cluster
        '''
        return len(self._items)

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
    def items(self):
        '''
        Return all the items stored by this cluster
        '''
        return self._items

    def add_item(self, item):
        self._items.append(item)
        logger.log('debug', "Added item {} from cluster {}".format(item.name, self.name))

    def remove_item(self, item):
        '''
        Remove the item from the items list
        '''
        self._items.remove(item)
        logger.log('debug', "Removed item {} from cluster {}".format(item.name, self.name))

    def contains(self, name):
        '''
        Returns whether this cluster contains the item given.
        Accepts the item name
        '''
        for item in self._items:
            if item.name == name:
                return True
        return False

    def as_itemcollection(self, copy=False):
        '''
        Return this cluster as an item collection.\n
        Args\n
        copy: If copy is set to True, then the returned ItemCollection will be a 
        deep copy of this cluster. Useful if you need to modify the resulting collection
        but do not want to affect this cluster. Will work slower than a shallow copy 
        '''
        attributes = OrderedSet()
        item_dict = {}
        if copy:
            item_dict = {item.name : item for item in self._items.copy()}
        else:
            item_dict = {item.name : item for item in self._items}
        if len(self._items) > 0:
            for attribute in self._items[0].attributes.keys():
                attributes.add(attribute)
        item_collection = ItemCollection(self.name)
        item_collection._items = item_dict
        item_collection._attributes = attributes
        return item_collection