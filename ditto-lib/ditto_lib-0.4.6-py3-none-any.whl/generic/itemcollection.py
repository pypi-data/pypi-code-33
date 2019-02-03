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
from sklearn.decomposition import PCA

from ditto_lib.generic.config import logger
from ditto_lib.generic.utils import percent_error, similarity_dict, error_dict, sqrt

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
        self._preamble = []
        self._items = {}
        self._name = name
    
    def __eq__(self, other):
        if self._attributes != other.attributes:
            logger.log('debug', "Attributes for {} and {} are not the same".format(self.name, other.name))
            return False
        for name, values in self._items.items():
            if not other.contains_item(name):
                logger.log('debug', "Item {} in {} but not in {}".format(name, self.name, other.name))
                return False
            for our_value, other_value in zip(values, other.items[name]):
                if our_value != other_value:
                    logger.log('debug', "Item {} does not contain same value for {} and {}".format(name, self.name, other.name))
                    return False
        for name, values in other._items.items():
            if not self.contains_item(name):
                logger.log('debug', "Item {} in {} but not in {}".format(name, other.name, self.name))
                return False
            for other_value, our_value in zip(values, self.items[name]):
                if other_value != our_value:
                    logger.log('debug', "Item {} does not contain same value for {} and {}".format(name, self.name, other.name))
                    return False
        return True
        
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

    @property
    def preamble(self):
        return self._preamble

    @preamble.setter
    def preamble(self, preamble):
        self._preamble = preamble

    def get_item(self, name):
        '''
        Return the item object that has the given name. Returns None
        if the item was not found
        '''
        if name in self._items:
            for idx in range(len(self._attributes)):
                if self._attributes[idx].is_descriptor:
                    self._items[name][idx] = float(self._items[name][idx])
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

    def strip(self, threshold=None):
        '''
        Remove any noisy attributes. Accepts a threshold, a number between 1 and 0. If 
        the percent of different values for a single attribute amongst all items is less
        than the threshold, remove it. Defaults to None, which will delete an attribute only if
        all items's share the same value for that attribute. Returns the name of the attributes
        that were stripped
        '''
        if threshold is None:
            threshold = 1/len(self._items)
        elif threshold < 0 or threshold > 1:
            logger.log('error', "Threshold must be 0 < threshold < 1")
            raise ValueError("Threshold must be 0 < threshold < 1")
        if len(self.items) > 0:
            logger.log('debug', "Stripping items from {} with a threshold of {}".format(self.name, threshold))
            to_strip = []
            for attribute in self.attributes:
                if attribute.is_descriptor:
                    unique_scores = set()
                    for item in self.items.values():
                        unique_scores.add(item[self.attributes.index(attribute)])
                    if len(unique_scores) / len(self._items) <= threshold:
                        to_strip.append(attribute.name)
            for attribute_name in to_strip:
                self.remove_attribute(attribute_name)
                logger.log('info', "Stripped {} from {}".format(attribute_name, self.name))
        logger.log('debug', "Stripped {} amount of attributes".format(len(to_strip)))
        return to_strip

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
            if attribute.is_descriptor:
                return float(self.get_item(item_name)[self.attributes.index(Attribute(attribute_name))])
            else:
                return self.get_item(item_name)[self.attributes.index(Attribute(attribute_name))]
        else:
            logger.log('error', "Could not find attribute {} in {}".format(attribute_name, self.name))
            raise ValueError("Could not find attribute {} in {}".format(attribute_name, self.name))

    def get_attribute(self, attribute_name):
        '''
        Get the attribue value of all items for the 
        attribute name given. Returns these values in a 
        list of tuples. The first item in the tuple contains
        the item name, the second item contains the attribute value
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self.attributes:
            logger.log('error', "Could not find attribute {} in {}".format(attribute_name, self.name))
            raise ValueError("Could not find attribute {} in {}".format(attribute_name, self.name))
        else:
            index = self.attributes.index(attribute)
            values = []
            for item_name, item in self.items.items():
                if self._attributes[index].is_descriptor:
                    values.append((item_name, float(item[index])))
                else:
                    values.append((item_name, item[index]))
            return values

    def attribute_index(self, attribute_name):
        '''
        Returns the index of the attribute name given. This
        can then be used to index items manually
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self.attributes:
            logger.log('error', "Could not find attribute {} in {}".format(attribute_name, self.name))
            raise ValueError("Could not find attribute {} in {}".format(attribute_name, self.name))
        else:
            return self.attributes.index(attribute)
            
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
                    self.add_attribute(attribute)
            self._items[item_name] = new_values
            logger.log('debug', "Added item {} with values {}".format(item_name, self._items[item_name]))


    def remove_item(self, item_name):
        '''
        Removes the item with the given name if it exists
        '''
        if self.contains_item(item_name):
            del self.items[item_name]

    def contains_item(self, item_name):
        '''
        Returns true if collection contains an item
        with the name given
        '''
        return item_name in self.items

    def contains_attribute(self, attribute_name):
        '''
        Returns true if the collection contains an
        attribute with the name give
        '''
        return Attribute(attribute_name) in self._attributes

    def get_sorted(self, attribute_name, descending=False):
        '''
        Return a list of tuples sorted by the given attribute name. 
        The first item in the tuple is the item name, the second item
        is the list of its features. Frames that don't have this attribute
        defined are sent to the back of the list
        '''
        attribute = Attribute(attribute_name)
        if attribute in self._attributes:
            if attribute.is_descriptor:
                index = self._attributes.index(attribute)
                for item in self._items.values():
                    item[index] = float(item[index])
            sort = sorted(self._items.keys(), key=lambda item : (self._items[item][self.attributes.index(attribute)] is None,
                self._items[item][self.attributes.index(attribute)]), reverse=descending)
            for index, item in enumerate(sort):
                sort[index] = (item, self._items[item][self.attributes.index(attribute)])
            return sort
        else:
            logger.log('error', "Tried to sort by {} which does not exist in container {}".format(attribute_name, self._name))
            raise ValueError("Tried to sort by {} which does not exist in container {}".format(attribute_name, self._name))

    def merge(self, collection, new_name, preamble_option='merge'):
        '''
        Return a collection that is the result of merging this
        collection and the one that is given. Merge attributes 
        and Data Frames\n

        Args:\n
        collection: The other collection to be merged with this one\n
        new_name: The name of the new collection\n
        preamble_option: Choose which collection's preamble to keep. None for neither, self for current collection,
        other for collection being passed as an argument, and merge for both.
        '''
        new_collection = ItemCollection(new_name)
        new_attributes = OrderedSet([self.attributes[i].copy() for i in range(len(self.attributes))])
        for i in range(len(collection.attributes)):
            new_attributes.add(collection.attributes[i].copy())
        logger.log('debug', "Attribute list {} generated".format([new_attributes[i].name for i in range(len(new_attributes))]))
        new_preamble = self._merge_preambles(collection, preamble_option)
        new_items = {}

        for name, values in self.items.items():
            new_values = values.copy()
            for index, attribute in enumerate(collection.attributes):
                if attribute not in self.attributes:
                    if collection.contains_item(name):
                        new_values.append(collection.items[name][index])
                    else:
                        new_values.append(None)
            new_items[name] = new_values

        for name, values in collection.items.items():
            if not self.contains_item(name):
                used = set()
                new_values = []
                for index, attribute in enumerate(self.attributes):
                    if attribute not in collection.attributes:
                        new_values.append(None)
                    else:
                        new_values.append(collection.items[name][collection.attributes.index(attribute)])
                        used.add(collection.attributes.index(attribute))
                for index, attribute in enumerate(collection.attributes):
                    if index not in used:
                        new_values.append(collection.items[name][index])
                new_items[name] = new_values
                
        new_collection._items = new_items
        new_collection._attributes = new_attributes
        new_collection._preamble = new_preamble
        return new_collection

    def intersect(self, collection, new_name, preamble_option='merge'):
        '''
        Intersects this collection's with the given collection's items.
        If the same item is contained in both collections, then the item 
        attributes are merged in this collection. Returns a new collection 
        a result\n
        Args:\n
        collection: The other collection to be merged with this one\n
        new_name: The name of the new collection\n
        preamble_option: Choose which collection's preamble to keep. None for neither, self for current collection,
        other for collection being passed as an argument, and merge for both.
        '''
        new_collection = ItemCollection(new_name)
        new_items = dict()
        new_attributes = OrderedSet([self.attributes[i].copy() for i in range(len(self.attributes))])
        new_preamble = self._merge_preambles(collection, preamble_option)
        for attributes in collection.attributes:
            new_attributes.add(attributes.copy())
        # Select items that are contained in both collections
        for name, values in self.items.items():
            if collection.contains_item(name):
                new_items[name] = values.copy()
        # Merge attributes
        used_indexes = set()
        for i in range(len(self.attributes)):
            attribute = self.attributes[i]
            if attribute in collection.attributes:
                used_indexes.add(collection.attributes.index(attribute))
                for name, values in self.items.items():
                    if values[i] == None:
                        values[i] = collection.items[name][collection.index(attribute)]
        for i in range(len(collection.attributes)):
            if i not in used_indexes:
                for name, values in new_items.items():
                    values.append(collection.items[name][i])
        new_collection._attributes = new_attributes
        new_collection._items = new_items
        new_collection._preamble = new_preamble
        return new_collection

    def copy(self, name):
        '''
        Return a deep copy of this collection with the name
        that is passed
        '''
        new_collection = ItemCollection(name)
        new_collection._attributes = OrderedSet([self._attributes[i].copy() for i in range(len(self.attributes))])
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
        self._preamble = []

    def from_csv(self, filename, start_row=0, start_column=1, non_descriptors=set(), encoding='utf-8-sig', preamble_indexes=None):
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
    
        non_descriptors: The set of names of any attributes that will not be descriptors in the 
        ItemCollection. Defaults to an empty set

        encoding: Defaults to 'utf-8-sig'

        preamble_indexes: A tuple, with the start row of the preamble, and the end row of the preamble. If
        there is no preamble, set to None. Defaults to None
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
        if preamble_indexes is not None:
            self._import_preamble(data_raw, preamble_indexes, start_row)

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
            self._items[arr[0]] = [item for item in arr[start_column:]]
        logger.log('info', "Imported {} from {}".format(self.name, filename))

    def to_csv(self, filename):
        '''
        Export this ItemCollection to the csv file given
        '''
        if '.csv' not in filename:
            filename += '.csv'
        with open(filename, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for preamble_row in self._preamble:
                csv_writer.writerow([thing for thing in preamble_row])
            csv_writer.writerow(['Name'] + [self._attributes[i].name for i in range(len(self._attributes))])
            for item_name, item in self.items.items():
                csv_writer.writerow([item_name] + 
                [attribute for attribute in item])
            logger.log('info', "{} written to {}".format(self.name, filename))

    def random_forest_classification(self):
        '''
        TO BE IMPLEMENTED
        '''
        pass
    
    def pca(self, n_components=None):
        '''
        PCA analysis\n
        Args:\n
        Number of components to keep. If set to None, all components are kept. Defaults to None
        '''
        collection, names = self.as_array()
        analysis = []
        pca = PCA(n_components=n_components)
        pca = pca.fit(collection[1]).explained_variance_ratio_
        for idx, name in enumerate(collection[0]):
            logger.log('debug', "Item {} with pca explained variance ratio {}".format(name, pca[idx]))
            analysis.append((name, pca[idx]))
        analysis.sort(key=lambda x: x[1], reverse=True)
        return analysis

    def as_array(self, excluded_attributes=set()):
        '''
        Return a list of all items. Items are represented by 
        their respective attribute values. Can pass a set of 
        attribute names that you don't want to include in the 
        raw data. Returns X, Y. Where X is the tuple (attribute names, 
        raw data). And Y is a list of the item names. Both the attribute
        names and item names are returned in order in accordance with the 
        raw data to easily understand the data.
        '''
        data_raw = []
        item_names = []
        attribute_names = []
        adding_attributes = True
        for item_name, item_data in self.items.items():
            descriptor_data = []
            for attribute in self.attributes:
                if attribute.is_descriptor and attribute.name not in excluded_attributes:
                    descriptor_data.append(float(item_data[self.attributes.index(attribute)]))
                    if adding_attributes is True:
                        attribute_names.append(attribute.name)
            adding_attributes = False
            data_raw.append(descriptor_data)
            item_names.append(item_name)
        return (attribute_names, data_raw), item_names

    def calc_error(self, target_score, actual_score, method='rmse'):
        '''
        Calculates an error value based on the given method for the entire collection.\n
        Args:\n
        target_score: The name of the target score attribute\n
        actual_score: The name of the actual score attribute\n
        method: The error calculation method to use. Options are rmse, mse. Defaults
        to rmse
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
        logger.log('debug', "Actual scores generated {}".format(actual_scores))
        logger.log('debug', "Target scores generated {}".format(target_scores))
        if method == 'rmse':
            return sqrt(error_dict['mse'](actual_scores, target_scores))
        else:
            return error_dict[method](actual_scores, target_scores)
    
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

    def calculate_similarity(self, first_item, second_item, method='euc'):
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
                    first_values.append(float(first_item[index]))
                    second_values.append(float(second_item[index]))
            logger.log('debug', "first_values {}, second_values {}".format(first_values, second_values))
            return similarity_dict[method](first_values, second_values)

    def calculate_all_similarities(self, item_name, method='euc'):
        '''
        Return a list of tuples where the first value is the 
        item it is being compared to, and the second value is the
        similarity score between the two items. Takes an item name.
        Returns the results by most similar to least similar.
        '''
        if item_name not in self._items:
            logger.log('error', "Could not find item {} in {}".format(item_name, self.name))
            'error', "Could not find item {} in {}".format(item_name, self.name)
        else:
            results = []
            for name in self.items.keys():
                if item_name != name:
                    results.append((name, self.calculate_similarity(item_name, name, method)))
            results.sort(key=lambda x: x[1], reverse=(method == 'cos' or method == 'jac'))
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

    def _import_preamble(self, data_raw, preamble_indexes, start_row):
        if start_row >= preamble_indexes[0] and start_row <= preamble_indexes[1]:
            logger.log('error', "Could not load preamble because indexes given coincided with the start row")
        else:
            for idx in range(preamble_indexes[1] - preamble_indexes[0] + 1):
                preamble_row = []
                for thing in data_raw[idx]:
                    preamble_row.append(thing)
                    logger.log('debug', "Adding {} to {}'s preamble".format(thing, self.name))
                self._preamble.append(preamble_row)

    def _merge_preambles(self, other, option):      
        if option == 'self':
            logger.log('debug', "New preamble will be current preamble")
            return [row.copy() for row in self._preamble]
        elif option == 'other':
            logger.log('debug', "New preamble will other's preamble")
            return [row.copy() for row in other._preamble]
        elif option is None:
            logger.log('debug', "New preamble will be empty")
            return []
        elif option is 'merge':
            logger.log('debug', "New preamble will be merged")
            new_preamble = [row.copy() for row in self._preamble]
            for other_row in other._preamble:
                for self_row in self._preamble:
                    if self_row != other_row:
                        new_preamble.append([thing.copy() for thing in other_row])
            return new_preamble
        else:
            logger.log('error', "Invalid preamble merge option given")
            return []
