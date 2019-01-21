#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  itemcollection.py
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements the a container to store Item objects.
#

import csv
import os.path
from ordered_set import OrderedSet
from sklearn.ensemble import RandomForestClassifier

from ditto_lib.generic.config import logger
from ditto_lib.generic.utils import percent_error, rmse, euclidean, stdev

class Attribute:

    def __init__(self, name, is_descriptor=True):
        self.is_descriptor = is_descriptor
        self.name = name
        self.hash = hash(name)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def copy(self):
        return Attribute(self.name, self.is_descriptor)

class ItemCollection:

    def __init__(self, name):
        self._attributes = OrderedSet()
        self._items = {}
        self._name = name
        
    @property
    def name(self):
        '''
        Name of the collection
        '''
        return self._name

    @name.setter
    def name(self, name):
        logger.log('debug', "{} name set to {}".format(self._name, name))
        self._name = name

    def __len__(self):
        '''
        Return how many items this collection is 
        storing
        '''
        return len(self._items)

    @property
    def attributes(self):
        '''
        Set of attribute names pertaining to this collection
        '''
        return self._attributes

    @property
    def items(self):
        '''
        Return all the dictionary of item name to items associated with this collection
        '''
        return self._items

    def get_item(self, name):
        '''
        Return the item object that has the given name. Returns None
        if the item was not found
        '''
        if name in self._items:
            return self._items[name]
        else:
            logger.log('error', "Could not get item {} from collection {}".format(name, self.name))
            raise ValueError("Could not get item {} from collection {}".format(name, self.name))

    def get_item_names(self):
        '''
        Return all the item names that are held by this 
        collection
        '''
        return self._items.keys()

    def strip(self):
        '''
        Remove all attributes from the collection that have the same 
        value for all items
        '''
        if len(self.items) > 0:
            logger.log('debug', "Stripping items from {}".format(self.name))
            to_strip = []
            first_item = self.items[next(iter(self.items))]
            for attribute in self.attributes:
                if attribute.is_descriptor:
                    score = first_item[self.attributes.index(attribute)]
                    same = True
                    for item in self.items.values():
                        if item[self.attributes.index(attribute)] != score:
                            same = False
                            break
                    if same is True:
                        to_strip.append(attribute.name)
            for attribute_name in to_strip:
                self.remove_attribute(attribute_name)
                logger.log('info', "Stripped {} from {}".format(attribute_name, self.name))

    def add_attribute(self, attribute):
        '''
        Adds an attribute to the ItemCollection. Adds this 
        attribute to all the items within the collection as well
        '''
        if attribute not in self._attributes:
            self._attributes.add(attribute)
            for item in self._items.values():
                item.append(None)
        logger.log('debug', "Added attribute {} to ItemCollection: {}".format(attribute.name, self._name))

    def remove_attribute(self, attribute_name):
        '''
        Remove the attribute from this collection and all items 
        stored in this collection as well. Takes an attribute name
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self.attributes:
            logger.log('error', "Could not remove {} because it doesn't exist in {}".format(attribute_name, self.name))
        else:
            for item in self.items.values():
                del item[self.attributes.index(attribute)]
            self.attributes.remove(attribute)

    def set_item_attribute(self, item_name, value, attribute_name, is_descriptor=True):
        '''
        Set the item's attribute to the given value. Adds this attribute if 
        the item doesn't contain it\n
        Args:\n
        item_name: The name of the item whose attribute is being modified/added\n
        attribute_name: The attribute being modified/added\n
        is_descriptor: Boolean whether the attribute is a descriptor, defaults to True
        '''
        attribute = Attribute(attribute_name, is_descriptor)
        if attribute not in self._attributes:
            logger.log('debug', "Could not find {} in {}, adding".format(attribute.name, self.name))
            self.add_attribute(attribute)
        if attribute.is_descriptor is True:
            self._items[item_name][self.attributes.index(attribute)] = float(value)
        else:
            self._items[item_name][self.attributes.index(attribute)] = value
        logger.log('debug', "Added attribute {} to item {}".format(attribute.name, item_name))

    def get_item_attribute(self, item_name, attribute_name):
        '''
        Get the item's attribute\n
        Args:\n
        item_name: The name of the item whose attribute is being retrieved\n
        attribute_name: The name of the attribute being retrieved\n
        '''
        attribute = Attribute(attribute_name)
        if attribute in self.attributes:
            return self.get_item(item_name)[self.attributes.index(Attribute(attribute_name))]
        else:
            logger.log('error', "Could not find attribute {} in {}".format(attribute_name, self.name))
            return None
            
    def add_item(self, item_name, values, attributes):
        '''
        Adds a item to the collection. Will mantain collection attribute 
        consistency amongst all items\n
        Args:\n
        item_name: Name of the item being added\n
        values: Values of the item being added\n
        attributes: The set of Attributes of the item being added
        '''
        if attributes == self.attributes:
            self._items[item_name] = values
        else:
            new_values = []
            used = set()
            for i in range(len(self.attributes)):
                if self.attributes[i] not in attributes:
                    new_values.append(None)
                else:
                    new_values.append(values[attributes.index(self.attributes[i])])
                    used.add(attributes.index(self.attributes[i]))
            for index, attribute in enumerate(attributes):
                if index not in used:
                    new_values.append(values[index])
                    self.attributes.add(attribute)
            self._items[item_name] = new_values
            logger.log('debug', "Added item {} with values {}".format(item_name, self._items[item_name]))


    def remove_item(self, item_name):
        '''
        Removes the item with the given name if it exists
        '''
        if self.contains(item_name):
            del self.items[item_name]

    def contains(self, item_name):
        '''
        Returns true if collection contains an item
        with the name given
        '''
        return item_name in self.items

    def get_sorted(self, attribute_name, descending=False):
        '''
        Return a list of tuples sorted by the given attribute name. 
        The first item in the tuple is the item name, the second item
        is the list of its features. Frames that don't have this attribute
        defined are sent to the back of the list
        '''
        attribute = Attribute(attribute_name)
        if attribute in self._attributes:
            sort = sorted(self._items.keys(), key=lambda item : (self._items[item][self.attributes.index(attribute)] is None,
                self._items[item][self.attributes.index(attribute)]), reverse=descending)
            for index, item in enumerate(sort):
                sort[index] = (item, self._items[item][self.attributes.index(attribute)])
            return sort
        else:
            logger.log('error', "Tried to sort by {} which does not exist in container {}".format(attribute_name, self._name))
            raise ValueError("Tried to sort by {} which does not exist in container {}".format(attribute_name, self._name))

    def merge_collections(self, collection, new_name):
        '''
        Return a collection that is the result of merging this
        collection and the one that is given. Merge attributes 
        and Data Frames\n

        Args:\n
        collection: The other collection to be merged with this one\n
        new_name: The name of the new collection
        '''
        return self._merge_helper(self, collection, new_name)

    def intersect(self, collection, new_name):
        '''
        Intersects this collection's with the given collection's items.
        If the same item is contained in both collections, then the item 
        attributes are merged in this collection. Returns a new collection 
        a result
        '''
        first_collection = self.copy("First Collection")
        second_collection = collection.copy("Second Collection")
        first_remove = []
        second_remove = []
        for name in first_collection.items.keys():
            if not second_collection.contains(name):
                first_remove.append(name)
        for name in second_collection.items.keys():
            if not first_collection.contains(name):
                second_remove.append(name)

        for name in first_remove:
            del first_collection.items[name]
        for name in second_remove:
            del second_collection.items[name]
        return self._merge_helper(first_collection, second_collection, new_name)

    def _merge_helper(self, first_collection, second_collection, name):
        new_collection = ItemCollection(name)
        new_attributes = OrderedSet([first_collection.attributes[i].copy() for i in range(len(self.attributes))])
        for i in range(len(second_collection.attributes)):
            new_attributes.add(second_collection.attributes[i].copy())
        logger.log('debug', "Attribute list {} generated".format([new_attributes[i].name for i in range(len(new_attributes))]))
        new_items = {}

        for name, values in first_collection.items.items():
            new_values = values.copy()
            for index, attribute in enumerate(second_collection.attributes):
                if attribute not in first_collection.attributes:
                    if second_collection.contains(name):
                        new_values.append(second_collection.items[name][index])
                    else:
                        new_values.append(None)
            new_items[name] = new_values

        for name, values in second_collection.items.items():
            if not first_collection.contains(name):
                used = set()
                new_values = []
                for index, attribute in enumerate(first_collection.attributes):
                    if attribute not in second_collection.attributes:
                        new_values.append(None)
                    else:
                        new_values.append(second_collection.items[name][second_collection.attributes.index(attribute)])
                        used.add(second_collection.attributes.index(attribute))
                for index, attribute in enumerate(second_collection.attributes):
                    if index not in used:
                        new_values.append(second_collection.items[name][index])
                new_items[name] = new_values
                
        new_collection._items = new_items
        new_collection._attributes = new_attributes
        return new_collection

    def copy(self, name):
        '''
        Return a deep copy of this collection with the name
        that is passed
        '''
        new_collection = ItemCollection(name)
        new_collection._attributes = OrderedSet([self._attributes[i] for i in range(len(self.attributes))])
        for item_name, item in self.items.items():
            new_collection.items[item_name] = item.copy()
        logger.log('debug', "{} copied to {}".format(self.name, new_collection.name))
        return new_collection

    def wipe(self):
        '''
        Wipe the current ItemCollection. Resetting its ItemCollections and
        attributes. Will keep the same name
        '''
        self._items = {}
        self._attributes = OrderedSet()

    def from_csv(self, filename, start_row=0, start_column=1, delimiter=',', encoding='utf-8-sig', non_descriptors=set(), cache_csv=True):
        '''
        Remove any data from this ItemCollection and import
        the data from a csv file

        Args:

        filename: The name of the csv file

        start_row: The start_row containing the name of the attributes. Defaults
        to 0. Anything under this will be assumed to be the items pertaining to 
        the current ItemCollection.

        start_column: The start_column containing the start of where the attribute values 
        will be located. Defaults to 0. If give a string, will look for that start_column name 
        and start importing values from that point. This method also assumes that the first 
        start_column of every csv file contains the item names

        delimiter: Delimiter that will be used, defaults to ','

        encoding: Encoding that will be used, defaults to 'utf-8-sig'
    
        non_descriptors: The set of names of any attributes that will not be descriptors in the 
        ItemCollection. Defaults to an empty set
        '''
        self.wipe()
        if '.csv' not in filename: 
            filename += '.csv'
        try:
            with open(filename, newline='') as file:
                data_raw = list(csv.reader(file))
        except FileNotFoundError:
            logger.log('error', "Could not find file {}".format(filename))
            raise FileNotFoundError("Couldn't find file {}".format(filename))

        # Check whether the start_column is a string, and find the correct value
        if isinstance(start_column, str):
            counter = 0
            for column in data_raw[start_row]:
                if start_column != column:
                    logger.log('debug', "Read start_column {}, moving to next one".format(start_column))
                    counter += 1
                else:
                    start_column = counter
                    logger.log('debug', "start_column set to {}".format(start_column))
                    break
            if not isinstance(start_column, int):
                logger.log('error', "Could not find start_column {}".format(start_column))
                raise ValueError("Could not find start_column {}".format(start_column))

        for name in data_raw[start_row][start_column:]:
            self._attributes.add(Attribute(name, name not in non_descriptors))
        logger.log('debug', "Attributes {} generated".format([self.attributes[i].name for i in range(len(self.attributes))]))
        for arr in data_raw[start_row + 1:]:
            self._items[arr[0]] = []
            for index, item in enumerate(arr[start_column:]):
                if self.attributes[index].is_descriptor:
                    self._items[arr[0]].append(float(item))
                else:
                    self._items[arr[0]].append(item)
        logger.log('info', "Imported {} from {}".format(self.name, filename))

    def to_csv(self, filename):
        '''
        Export this ItemCollection to the csv file given
        '''
        if '.csv' not in filename:
            filename += '.csv'
        with open(filename, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Name'] + [self._attributes[i].name for i in range(len(self._attributes))])
            for item_name, item in self.items.items():
                csv_writer.writerow([item_name] + 
                [attribute for attribute in item])
            logger.log('info', "{} written to {}".format(self.name, filename))

    def random_forest_classification(self, n_components, target_attribute, n_estimators=200):
        '''
        Return attributes of each item in the collection and
        in the order of their importance based on a random forest
        analysis.\n
        Args:\n
        n_components: The number of attributes returned in the list\n
        target_attribute: The target output value for each feature set input, should be a non
        descriptive attribute name\n
        n_estimators: The number of trees in a forest.
        '''
        logger.log('debug', "Running feature selection for {}".format(self.name))
        attributes = self.get_descriptive_attributes()
        data_raw, item_names = self.as_array()
        target_values = [int(item) for item in self.items.values()]
        if len(target_values) != len(data_raw):
            logger.log('error', "Target values != Amount of input")
            raise ValueError("Target values != Amount of input")
        clf = RandomForestClassifier(n_estimators=n_estimators, oob_score=True, random_state=0)
        clf.fit(data_raw, target_values)
        final_data = []
        for index, attribute in enumerate(attributes):
            final_data.append((attribute.name, clf.feature_importances_[index]))
        final_data.sort(key=lambda x: x[1], reverse=True)
        logger.log('info', "Ran feature selection for {}".format(self.name))
        return final_data[:n_components]

    def as_array(self):
        '''
        Return a list of all items. Items are represented by 
        their respective attribute values
        '''
        data_raw = []
        item_names = []
        for item_name, item_data in self.items.items():
            descriptor_data = []
            for attribute in self.attributes:
                if attribute.is_descriptor:
                    descriptor_data.append(float(item_data[self.attributes.index(attribute)]))
            data_raw.append(descriptor_data)
            item_names.append(item_name)
        return data_raw, item_names

    def calc_rmse(self, target_score, actual_score):
        '''
        Generate an rmse value\n
        Args:\n
        target_score: The name of the target score attribute\n
        actual_score: The name of the actual score attribute\n
        '''
        target_att = Attribute(target_score)
        actual_att = Attribute(actual_score)
        if target_att not in self.attributes or actual_att not in self.attributes:
            logger.log('error', "{} or {} not in collection {}".format(target_score, actual_score, self.name))
            raise ValueError("{} or {} not in collection {}".format(target_score, actual_score, self.name))
        target_scores = []
        actual_scores = []
        for item in self.items.values():
            target_scores.append(float(item[self.attributes.index(target_att)]))
            actual_scores.append(float(item[self.attributes.index(actual_att)]))
        return rmse(target_scores, actual_scores)
    
    def generate_error(self, name, target_score, actual_score):
        '''
        Generate the percent error of one attribute compared to another
        attribute for every item in the collection.\n
        Args:\n
        name: The name of the new attribute where the result will be stored\n
        target_score: The target score that will be compared to the actual score\n
        actual_score: The actual score that will be compared to the target score
        '''
        target_att = Attribute(target_score)
        actual_att = Attribute(actual_score)
        if target_att not in self.attributes or actual_att not in self.attributes:
            logger.log('error', "{} or {} not in collection {}".format(target_score, actual_score, self.name))
            raise ValueError("{} or {} not in collection {}".format(target_score, actual_score, self.name))
        self.attributes.add(Attribute(name, False))
        for item_name, item in self.items.items():
            target = float(item[self.attributes.index(target_att)])
            actual = float(item[self.attributes.index(actual_att)])
            error = percent_error(actual, target)
            item.append(error)
            logger.log('debug', "Percent error: {}, found between target score {} and actual score {} for item {}".format(error,
                target_score, actual_score, item_name))

    def calculate_similarity(self, first_item, second_item):
        '''
        Calculate the similarity between two items in a collection
        '''
        if first_item not in self.items or second_item not in self.items:
            logger.log('error', "Could not find {} or {} in {}".format(first_item, second_item, self.name))
            raise ValueError("Could not find {} or {} in {}".format(first_item, second_item, self.name))
        else:
            first_item = self.get_item(first_item)
            second_item = self.get_item(second_item)
            first_values = []
            second_values = []
            for index, attribute in enumerate(self.attributes):
                if attribute.is_descriptor:
                    first_values.append(first_item[index])
                    second_values.append(second_item[index])
            logger.log('debug', "first_values {}, second_values {}".format(first_values, second_values))
            return euclidean(first_values, second_values)

    def calculate_all_similarities(self, item_name):
        '''
        Return a list of tuples where the first value is the 
        item it is being compared to, and the second value is the
        similarity score between the two items. Takes an item name
        '''
        item = self.get_item(item_name)
        results = []
        for name, other_item in self.items.items():
            if item_name != name:
                results.append((name, self.calculate_similarity(item_name, name)))
        return results

    def get_descriptive_attributes(self):
        '''
        Return all attributes that are considered desciptors
        '''
        attributes = []
        for attribute in self.attributes:
            if attribute.is_descriptor:
                attributes.append(attribute.name)
        return attributes