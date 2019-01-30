"""Contains the DataObject class for storing, accessing, and processing data for ML"""

import json
import os
import numpy as np


class DataObject:
    """Handles all data manipulation and access through a unified tree-structure model."""

    def __init__(self, value, singular=False, recursion_depth=-1, **properties):
        """Construct a DataObject from the value that should be contained in it.

        Args:
            value (object): value to encapsulate
            singular (bool, optional): defaults to False. Equivalent to recursion_depth==0. Determines whether value structure should be maintained
            recursion_depth (int, optional): defaults to -1. Determines at what level value structure should be maintained
        """

        # Check if singular flag is raised and set recursion depth appropriately
        if singular:
            if recursion_depth != -1:
                raise ValueError("Both singular and recursion_depth parameters were set. Set only one parameter.")
            recursion_depth = 0

        try:
            # If no recursion, default to singular
            # Default string to singular
            if recursion_depth == 0 or isinstance(value, str):
                raise TypeError()

            try:
                # Set value to plural pandas input value
                self.value = {index: value.loc[index] if isinstance(value.loc[index], DataObject)
                              else DataObject(value.loc[index], recursion_depth=recursion_depth - 1)
                              for index in value.index}
                self.container = True
                self.dict = True
            except:
                try:
                    # Set value to plural dict-like input value
                    self.value = {sub_key:
                                  (sub_value if isinstance(sub_value, DataObject) else
                                   DataObject(sub_value, recursion_depth=recursion_depth - 1))
                                  for sub_key, sub_value in zip(value.keys(), value.values())}
                    self.container = True
                    self.dict = True

                except:
                    # Set value to plural list-like input value
                    self.value = [sub_value if isinstance(sub_value, DataObject) else
                                  DataObject(sub_value, recursion_depth=recursion_depth - 1)
                                  for sub_value in value]
                    self.container = True
                    self.dict = False
        except TypeError:
            # Set value to singular input value
            self.value = value
            self.container = False
            self.dict = False

        # Calculate the shape of the data
        self.shape = self.__calculate_shape()

        # Set properties on object
        for prop_name, prop_value in zip(properties.keys(), properties.values()):
            setattr(self, prop_name, prop_value)

    def __eq__(self, obj):
        """Checks equality between this and other object

        Args:
            obj (object): object to check equality with

        Returns:
            bool: objects are equal
        """

        if self.container:
            # Perform plural value comparison
            try:
                # Return false if comparable object has different length
                if len(obj) != len(self.value):
                    return False

                if self.dict:
                    # Return false if comparable object has any different elements in dict form
                    for sub_key, sub_value in zip(obj.keys(), obj.values()):
                        if sub_key not in self.value or self.value[sub_key] != sub_value:
                            return False
                else:
                    # Return false if comparable object has any different elements in list form
                    for sub_value in obj:
                        if sub_value not in self.value:
                            return False

                # Return true if all equality checks pass
                return True

            # Return false if comparable object is not dict
            except TypeError:
                return False
        else:
            # Perform singular value comparison
            try:
                # Return comparison between two DataObjects
                return self.value == obj.value
            except AttributeError:
                # Return comparison between two values
                return self.value == obj

    def __ne__(self, obj):
        """Checks inequality between this and other object

        Args:
            obj (object): object to check inequality with

        Returns:
            bool: objects are not equal
        """

        return not self == obj

    def __int__(self):
        """Convert object to integer.

        Returns:
            int: integer representation
        """

        return int(self.value)

    def __float__(self):
        """Convert object to floating point number.

        Returns:
            float: float representation
        """

        return float(self.value)

    def __complex__(self):
        """Convert object to complex floating point number.

        Returns:
            complex: complex representation
        """

        return complex(self.value)

    def __str__(self):
        """Convert object to string.

        Returns:
            str: string representation
        """

        return str(self.value)

    def __bytes__(self):
        """Convert object to bytes.

        Returns:
            bytes: bytes representation
        """

        return bytes(self.value)

    def __bool__(self):
        """Convert object to boolean.

        Returns:
            bool: boolean representation
        """

        return bool(self.value)

    def __repr__(self):
        """Get representation of object

        Returns:
            str: object representation
        """

        return repr(self.value)

    def __iter__(self):
        """Get iterator over object.

        Returns:
            iter: iterator of object value
        """

        return iter(self.value)

    def __len__(self):
        """Get length of object.

        Returns:
            int: length of object
        """

        return len(self.value)

    def __contains__(self, obj):
        """Determine if another object is in this.

        Args:
            obj (object): object to check for membership

        Returns:
            bool: object is in this
        """

        return obj in self.value

    def __getitem__(self, key):
        """Get a subset of the object.

        Args:
            key (int, str, iterable): key to index

        Returns:
            object: indexed value of object
        """

        def get_tuple(key):
            """Get tuple subset of object

            Args:
                key (tuple): tuple index

            Returns:
                object: indexed value of object
            """

            # Return entire object for empty tuple key for consistency with ellipses
            if not key:
                return self

            # Return default item for tuples of single length (base case for deep-indexing recursion)
            if len(key) == 1:
                # Special permutation case of ellipses
                if key[0] is Ellipsis:
                    return self.__index_ellipsis(())
                return self[key[0]]

            try:
                # Override string iterable and treat as singular
                if isinstance(key[0], str):
                    raise TypeError()

                # Return slice key deep-indexing
                if isinstance(key[0], slice):
                    return DataObject([sub_value[key[1:]] for sub_value in self[key[0]]], recursion_depth=1)

                # Return ellipsis key deep-indexing
                if key[0] is Ellipsis:
                    return self.__index_ellipsis(key[1:])

                    # Return iterable key deep-indexing
                return DataObject([self[sub_key][key[1:]] for sub_key in key[0]], recursion_depth=1)

            except:
                # Return singular key deep-indexing
                return self[key[0]][key[1:]]

        try:
            # Handle deep-indexing for tuple keys
            if isinstance(key, tuple):
                return get_tuple(key)

            # Handle indexing for slice keys
            elif isinstance(key, slice):
                return DataObject([sub_value for sub_value in self.value[key]], recursion_depth=1)

            # Handle indexing for boolean keys
            elif isinstance(key, bool):
                if key:
                    return self
                return None

            else:
                # Override string iterable and treat as singular
                if isinstance(key, str):
                    raise TypeError()

                # Return iterable key representation
                try:
                    # Dictionary representation
                    sub_keys = key.keys()
                    sub_vals = key.values()
                    return DataObject({sub_key: self.value[sub_key][sub_val] for sub_key, sub_val in
                                       zip(sub_keys, sub_vals) if (not isinstance(sub_val, bool) or sub_val)}, recursion_depth=1)

                except:
                    # Boolean list representation
                    if all(isinstance(sub_key, bool) for sub_key in key):
                        return DataObject([self[sub_index, sub_key] for sub_index, sub_key in enumerate(key) if sub_key], recursion_depth=1)

                    # Default list representation
                    return DataObject([self[sub_key] for sub_key in key], recursion_depth=1)

        except (TypeError, LookupError):
            try:
                # Return singular key representation
                return self.value[key]
            except:
                # Return broadcasted index representation
                if self.dict:
                    return DataObject({sub_key: sub_val[key] for sub_key, sub_val in
                                       zip(self.value.keys(), self.value.values())}, recursion_depth=1)
                return DataObject([sub_val[key] for sub_val in self.value], recursion_depth=1)

    def __setitem__(self, key, val):
        """Set a subset of the object.

        Args:
            key (int, str, iterable): key to index
            val (object): value to set at index
        """

        if self.container:
            # Try setting when sub-object is DataObject
            sub_object = self[key]
            if sub_object.container:
                try:
                    # Override default iterable behavior of strings
                    if isinstance(val, str):
                        raise TypeError()

                    # Check to make sure that shapes match
                    if len(val) != len(sub_object):
                        raise ValueError("Shape of value does not match shape of indexed object.")

                    # Set each value in the sub-object to each sub-value of the value passed in
                    for set_index, set_value in enumerate(val):
                        sub_object[set_index] = set_value

                except TypeError:
                    # Broadcast value to all children of the indexed item
                    for sub_index in sub_object.value.keys() if sub_object.dict else range(len(sub_object)):
                        sub_object[sub_index] = val
            else:
                # Pass value to indexed item
                sub_object.value = val
        else:
            # Try setting if sub-object is not DataObject
            try:
                # Try iterable key iterable value
                try:
                    for sub_key, sub_value in zip(key, val):
                        self.value[sub_key] = sub_value
                # Try iterable key singular value
                except TypeError:
                    for sub_key in key:
                        self.value[sub_key] = val
            except:
                # Try default key
                self.value[key] = val

    def __getattr__(self, attr):
        """Get a specified attribute of the object

        Args:
            attr (str): attribute to get

        Raises:
            AttributeError: raised when attribute does not exist

        Returns:
            object: object containing results of accession
        """

        try:
            # Try to get attribute from stored value
            return getattr(self.value, attr)

        except AttributeError:
            if self.container:
                # Try to get attribute from each element of the object
                return DataObject({sub_key: getattr(sub_value, attr) for sub_key, sub_value in
                                   zip(self.value.keys(), self.value.values())} if self.dict else
                                  [getattr(sub_value, attr) for sub_value in self.value], recursion_depth=1)

            # Attempt to access attribute failed so raise error
            raise

    def __setattr__(self, attr, val):
        """Set a specified attribute of the object

        Args:
            attr (str): attribute to set
            val (object): attribute value
        """

        # If attribute is a class attribute, set it on the object
        if attr in ('value', 'container', 'dict', 'shape'):
            super().__setattr__(attr, val)
        else:
            try:
                # Try setting attribute on value of object
                setattr(self.value, attr, val)

            except AttributeError:
                # Attempt recursively passing down attributes
                if self.container:
                    try:
                        # Override the default iterable behavior of strings
                        if isinstance(val, str):
                            raise TypeError()

                        # Set values of dictionary based on keys
                        if self.dict:
                            for sub_key, sub_value in zip(val.keys(), val.values()):
                                setattr(self[sub_key], attr, sub_value)

                        # Set values of list based on indices
                        else:
                            if len(val) != len(self):
                                raise ValueError()

                            for sub_index, sub_value in enumerate(val):
                                setattr(self[sub_index], attr, sub_value)

                    # Handle exceptions by setting value on object
                    except (TypeError, ValueError):
                        super().__setattr__(attr, val)

                # Handle singular objects by setting value on object
                else:
                    super().__setattr__(attr, val)

    def __call__(self, parameters=None):
        """Call the function contained in the object
            parameters (obj, optional): Defaults to None. A hierarchical structure of parameters to pass to contained methods.

        Returns:
            DataObject: object containing results of calling each function
        """

        if self.container:
            if parameters is None:
                # Return default method results for dict recursively
                if self.dict:
                    return DataObject(
                        {sub_key: sub_value() for sub_key, sub_value in
                         zip(self.value.keys(), self.value.values())}, recursion_depth=1)
                # Return default method results for list recursively
                return DataObject(
                    [sub_value() for sub_value in self.value], recursion_depth=1)

            try:
                # Override the default iterable behavior of strings
                if isinstance(parameters, str):
                    raise TypeError()

                if self.dict:
                    # Return dict results with recursive parameters
                    return DataObject(
                        {sub_key: sub_value(parameters[sub_key]) for sub_key, sub_value in
                         zip(self.value.keys(), self.value.values())}, recursion_depth=1)
                else:
                    # Check that shapes match to avoid half-indexing unintentionally
                    if len(parameters) != len(self):
                        raise ValueError()

                    # Return list results with recursive parameters
                    return DataObject(
                        [sub_value(parameters[sub_index]) for sub_index, sub_value in
                         enumerate(self.value)], recursion_depth=1)

            except:
                # Return dict results when broadcasting parameters
                if self.dict:
                    return DataObject(
                        {sub_key: sub_value(parameters) for sub_key, sub_value in
                         zip(self.value.keys(), self.value.values())}, recursion_depth=1)

                # Return list results when broadcasting parameters
                return DataObject(
                    [sub_value(parameters) for sub_value in self.value], recursion_depth=1)
        else:
            # Return default method results with no parameters
            if parameters is None:
                return self.value()

            # Return method results with parameters
            return self.value(*parameters)

    def __hash__(self):
        """Create a hash code of the object

        Returns:
            int: hash code
        """

        if self.container:
            if self.dict:
                return hash(tuple(self.value.items()))
            return hash(tuple(self.value))
        return hash(self.value)

    def __calculate_shape(self):
        """Calculate the shape of the data recursively

        Returns:
            tuple or dict: recursive representation of data shape as tuples and dicts
        """

        # Construct shape recursively
        if self.container:
            if self.dict:
                # Get dict of sub-shapes
                sub_shape = dict((sub_key, sub_value.shape if isinstance(sub_value, DataObject) else 1)
                                 for sub_key, sub_value in zip(self.value.keys(), self.value.values()))

                # Replace multiple single element sizes with a combined key tuple
                if all(map(lambda x: x == 1, sub_shape.values())):
                    return tuple(sub_shape.keys())
                return sub_shape

            else:
                # Get tuple of sub-shapes
                sub_shape = tuple(sub_value.shape if isinstance(sub_value, DataObject) else 1
                                  for sub_value in self.value)

                # Replace multiple single element sizes with a combined length
                #   Create a cumulative combined shape
                combined_shape = ()
                combined_length = 0

                #   Iterate through the uncombined shape and replace series of ones with the number of ones
                for element in sub_shape:
                    if element == 1:
                        combined_length += 1
                    elif combined_length:
                        combined_shape = combined_shape + (combined_length, ) + (element, )
                        combined_length = 0
                    else:
                        combined_shape = combined_shape + (element, )
                if combined_length:
                    combined_shape = combined_shape + (combined_length, )

                # Return new combined shape
                return combined_shape

        # Shape is one for singular values
        return 1

    def flatten(self, once=False, recursion_depth=-1):
        """Flatten the object in a top-down fashion recursively.
            once (bool, optional): Defaults to False. Whether the object should only be flattened once.
            recursion_depth (int, optional): Defaults to -1. The number of layers to recursively flatten.

        Raises:
            TypeError: Raised if some children objects cannot be merged together due to type issues.
            ValueError: Raised if the object that is being flattened is represented by a dictionary.

        Returns:
            DataObject: The flattened object.
        """

        # Check if once flag was set
        if once:
            # Check if recursion depth was also set and raise warning if so
            if recursion_depth != -1:
                raise ValueError("Both once and recursion_depth parameters were set. Set only one parameter.")
            recursion_depth = 1

        # Stop recursion if flattened to specified amount
        if recursion_depth == 0:
            return [self.value]

        # Recursively flatten container
        try:
            if self.container:
                if self.dict:
                    raise ValueError()
                return DataObject(sum((list(sub_value.flatten(recursion_depth=recursion_depth - 1))
                                       for sub_value in self.value), []), recursion_depth=1)
            return [self.value]

        # Exceptions for invalid flattenings
        except TypeError:
            raise TypeError(f"Incompatible children DataObject types.")
        except ValueError:
            raise ValueError(f"Cannot flatten dict type.")

    @staticmethod
    def json_from_dataobject(dataobject):
        """Convert a DataObject instance into JSON saveable format.

        Args:
            dataobject (DataObject): DataObject to convert

        Returns:
            dict: JSON formatted hierarchy
        """

        try:
            return dataobject.item()
        except:
            if isinstance(dataobject, DataObject):
                do_dict = {k: DataObject.json_from_dataobject(dataobject.__dict__[k])
                           for k in dataobject.__dict__ if k not in ('dict', 'shape')}

                if dataobject.container:
                    if dataobject.dict:
                        do_dict['value'] = {k: DataObject.json_from_dataobject(do_dict['value'][k]) for k in do_dict['value']}
                    else:
                        do_dict['value'] = [DataObject.json_from_dataobject(v) for v in do_dict['value']]
                elif isinstance(dataobject.value, np.ndarray):
                    do_dict['value'] = dataobject.value.tolist()
                return do_dict
            elif isinstance(dataobject, np.ndarray):
                return {
                    'value': dataobject.tolist(),
                    '_array_': True
                }
            elif isinstance(dataobject, dict):
                return {k: DataObject.json_from_dataobject(dataobject[k]) for k in dataobject}
            elif isinstance(dataobject, list):
                return [DataObject.json_from_dataobject(v) for v in dataobject]
            else:
                return dataobject

    @staticmethod
    def dataobject_from_json(json_data):
        """Convert JSON data to a DataObject

        Args:
            json_data (dict): Valid JSON formatted data hierarchy

        Returns:
            DataObject: Corresponding evaluation of JSON format
        """

        if isinstance(json_data, dict):
            props = {k: DataObject.dataobject_from_json(json_data[k]) for k in json_data if k not in ('value', 'container', '_array_')}
            if ('value' in json_data) and ('container' in json_data):
                if json_data['container']:
                    if isinstance(json_data['value'], dict):
                        return DataObject({key: DataObject.dataobject_from_json(json_data['value'][key])
                                            for key in json_data['value']}, recursion_depth=1, **props)
                    return DataObject([DataObject.dataobject_from_json(sub_value)
                                        for sub_value in json_data['value']], recursion_depth=1, **props)
                else:
                    return DataObject(json_data['value'], singular=True, **props)
            elif ('value' in json_data) and ('_array_' in json_data):
                return DataObject(np.array(json_data['value']), singular=True, **props)
            else:
                return DataObject(None, **props)
        else:
            return DataObject(json_data, singular=True)

    @staticmethod
    def save_to(dataobject, path):
        """Save DataObject to a specific path as a JSON file.

        Args:
            dataobject (DataObject): DataObject to be saved
            path (str): Path to file to be written
        """

        if os.path.dirname(path) != '' and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        with open(path, "w") as out_file:
            json.dump(DataObject.json_from_dataobject(dataobject), out_file)

    @staticmethod
    def load_from(path):
        """Load DataObject from a specific path as a JSON file.

        Args:
            path (str): Path to file to be read

        Returns:
            DataObject: DataObject loaded from file
        """

        with open(path, "r") as in_file:
            json_data = json.load(in_file)
        return DataObject.dataobject_from_json(json_data)

    def save(self, path):
        """Save DataObject to specified path.

        Args:
            path (str): Path to file to be written
        """

        DataObject.save_to(self, path)
