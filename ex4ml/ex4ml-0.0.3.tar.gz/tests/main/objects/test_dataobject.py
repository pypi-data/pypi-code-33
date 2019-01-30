"""Tests for the DataObject class
"""

import pytest
import os
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from ex4ml.objects.dataobject import DataObject


def test_default_singular_number():
    """Test common functions of a number that should default to singular
    """

    # Create numeric singular data object
    singular = DataObject(1)

    # Equality operator
    assert singular == 1
    # Inequality operator
    assert singular != 2
    # Inequality based on shape
    assert singular != [1]
    # Correct value construction
    assert singular.value == 1
    # Correct singular construction
    assert not singular.container
    # String interpretation
    assert str(singular) == '1'
    # Representative interpretation
    assert repr(singular) == '1'


def test_default_singular_string():
    """Test common functions of a string that should default to singular
    """

    # Create string singular data object
    singular = DataObject("data")

    # Proper length
    assert len(singular) == len("data")
    # Equality operator
    assert singular == "data"
    # Inequality operator
    assert singular != "apple"
    # Inequality based on shape
    assert singular != ["data"]
    # Correct value construction
    assert singular.value == "data"
    # Correct singular construction
    assert not singular.container
    # String interpretation
    assert str(singular) == "data"
    # Representative interpretation
    assert repr(singular) == "'data'"

    # Test string specific functions

    # Test iteration on data object
    assert all(x == y for x, y in zip(singular, "data"))
    # Containment operator
    assert 'a' in singular
    # Non-containment operator
    assert 'b' not in singular
    # Get indexing
    assert singular[1] == 'a'
    assert singular[2] == 't'
    # Set indexing
    with pytest.raises(TypeError):
        singular[1] = 'o'
    # Broadcasting to value
    assert singular.lower
    assert singular.upper


def test_forced_singular_list():
    """Test common functions of a list that is forced to singular
    """

    # Create list singular data object
    list_singular = DataObject([1, 2, 3], singular=True)

    # Proper length
    assert len(list_singular) == 3
    # Equality operator
    assert list_singular == [1, 2, 3]
    # Inequality operator
    assert list_singular != [1, 2, 4]
    # Inequality based on shape
    assert list_singular != [[1, 2, 3]]
    assert list_singular != [[1], [2], [3]]
    # Correct value construction
    assert list_singular.value == [1, 2, 3]
    # Correct singular construction
    assert not list_singular.container
    # Containment operator
    assert 1 in list_singular
    # Non-containment operator
    assert 4 not in list_singular
    # String interpretation
    assert str(list_singular) == '[1, 2, 3]'
    # Representative interpretation
    assert repr(list_singular) == '[1, 2, 3]'

    # Test iteration on values
    assert all(x == y for x, y in zip(list_singular, [1, 2, 3]))
    # Test value type
    assert isinstance(list_singular.value, list)
    # Test value element type
    assert all(isinstance(x, int) for x in list_singular)

    # Get indexing integer
    assert list_singular[0] == 1
    assert list_singular[2] == 3
    # Get indexing slice
    assert list_singular[:2] == [1, 2]
    assert list_singular[::2] == [1, 3]
    # Get indexing iterable
    assert list_singular[[2, 1, 1]] == [3, 2, 2]

    # Set indexing integer
    list_singular[0] = 0
    assert list_singular == [0, 2, 3]
    list_singular[2] = 4
    assert list_singular == [0, 2, 4]
    # Set indexing slice
    list_singular[:2] = [1, 3]
    assert list_singular == [1, 3, 4]
    list_singular[::2] = [2, 5]
    assert list_singular == [2, 3, 5]
    # Set indexing iterable
    list_singular[[2, 1, 1]] = [4, 2, 1]
    assert list_singular == [2, 1, 4]
    list_singular[[2, 1]] = 0
    assert list_singular == [2, 0, 0]

    # Broadcasting to value
    assert list_singular.append
    assert list_singular.remove


def test_forced_singular_dict():
    """Test common functions of a dict that is forced to singular
    """

    dict_singular = DataObject({'a': 1, 'b': 2, 'c': 3}, singular=True)

    # Proper length
    assert len(dict_singular) == 3
    # Equality operator
    assert dict_singular == {'a': 1, 'b': 2, 'c': 3}
    # Inequality operator
    assert dict_singular != {'a': 1, 'b': 2, 'c': 4}
    assert dict_singular != {'a': 1, 'b': 2, 'd': 3}
    # Inequality based on shape
    assert dict_singular != [{'a': 1, 'b': 2, 'c': 3}]
    assert dict_singular != {'a': [1], 'b': [2], 'c': [3]}
    # Correct value construction
    assert dict_singular.value == {'a': 1, 'b': 2, 'c': 3}
    # Correct singular construction
    assert not dict_singular.container
    # Containment operator
    assert 'a' in dict_singular
    # Non-containment operator
    assert 'd' not in dict_singular
    # String interpretation
    assert str(dict_singular) == "{'a': 1, 'b': 2, 'c': 3}"
    # Representative interpretation
    assert repr(dict_singular) == "{'a': 1, 'b': 2, 'c': 3}"

    # Test iteration on values
    assert all(x in ['a', 'b', 'c'] for x in dict_singular)
    # Test value type
    assert isinstance(dict_singular.value, dict)
    # Test value element type
    assert all(isinstance(x, str) for x in dict_singular)
    assert all(isinstance(dict_singular[x], int) for x in dict_singular)

    # Get indexing string
    assert dict_singular['a'] == 1
    assert dict_singular['c'] == 3
    # Get indexing iterable
    assert dict_singular[['c', 'b', 'b']] == [3, 2, 2]

    # Set indexing string
    dict_singular['a'] = 0
    assert dict_singular == {'a': 0, 'b': 2, 'c': 3}
    dict_singular['c'] = 4
    assert dict_singular == {'a': 0, 'b': 2, 'c': 4}
    # Set indexing iterable
    dict_singular[['c', 'b', 'b']] = [4, 2, 1]
    assert dict_singular == {'a': 0, 'b': 1, 'c': 4}

    # Broadcasting to value
    assert dict_singular.keys
    assert dict_singular.values


def test_singular_recursion_error():
    """Test that an error is thrown in the construction of a data object if
    both singular and recursion_depth are specified
    """
    with pytest.raises(ValueError):
        DataObject([1, 2, 3], singular=True, recursion_depth=1)


def test_container_list():
    """Test common functions of a container list
    """

    # Create list data object with corresponding target list
    data = [0, 1, 2, 5, 6, 7, 8, 10]
    target = [0, 1, 1, 0, 0, 1, 0, 0]
    data_object = DataObject(data, target=target)

    # Equality operator
    assert data_object == [0, 1, 2, 5, 6, 7, 8, 10]
    # Inequality operator
    assert data_object != [0, 1, 3, 5, 6, 7, 8, 10]
    # Inequality based on shape
    assert data_object != [[0, 1, 2, 5, 6, 7, 8, 10]]
    assert data_object != [[0], [1], [2], [5], [6], [7], [8], [10]]

    # Iteration
    assert all(x == y for x, y in zip(data_object, data))
    # Correct length
    assert len(data_object) == 8
    # Correct value construction
    assert data_object.value == [0, 1, 2, 5, 6, 7, 8, 10]
    # Correct container construction
    assert data_object.container

    # Correct types
    assert isinstance(data_object.value, list)
    assert all(isinstance(x, DataObject) for x in data_object)
    assert all(isinstance(x.value, int) for x in data_object)

    # Containment operator
    assert 0 in data_object
    assert 5 in data_object
    # Non-containment operator
    assert 3 not in data_object
    assert 9 not in data_object

    # String interpretation
    assert str(data_object) == '[0, 1, 2, 5, 6, 7, 8, 10]'
    # Representative interpretation
    assert repr(data_object) == '[0, 1, 2, 5, 6, 7, 8, 10]'

    # Correct property recursion
    assert data_object.target == [0, 1, 1, 0, 0, 1, 0, 0]
    for i, data_subobject in enumerate(data_object):
        assert data_subobject.target == data_object.target[i]

    # Get indexing integer
    assert data_object[1] == 1
    assert data_object[5] == 7
    # Get indexing slice
    assert data_object[2:6] == [2, 5, 6, 7]
    assert data_object[:-4:-1] == [10, 8, 7]
    # Get indexing iterable
    assert data_object[[0, 3, 7]] == [0, 5, 10]
    assert data_object[[2, 1, 2, 4]] == [2, 1, 2, 6]

    # Set indexing integer
    data_object[2] = 9
    assert data_object == [0, 1, 9, 5, 6, 7, 8, 10]
    data_object[7] = 1
    assert data_object == [0, 1, 9, 5, 6, 7, 8, 1]
    # Set indexing slice
    data_object[3:5] = [8, 7]
    assert data_object == [0, 1, 9, 8, 7, 7, 8, 1]
    data_object[1::2] = [2, 3, 4, 5]
    assert data_object == [0, 2, 9, 3, 7, 4, 8, 5]
    # Set indexing iterable
    data_object[[1, 4, 5]] = [10, 9, 8]
    assert data_object == [0, 10, 9, 3, 9, 8, 8, 5]
    data_object[[0, 6, 6]] = [5, 4, 2]
    assert data_object == [5, 10, 9, 3, 9, 8, 2, 5]
    data_object[[0, 1]] = 0
    assert data_object == [0, 0, 9, 3, 9, 8, 2, 5]

    # Broadcasting to value
    assert data_object.append
    assert data_object.remove


def test_container_dict():
    """Test common functions of a container dict
    """

    # Create dict data object with corresponding target dict
    data = {'a': 'apple', 'b': 'banana', 'c': 'cherry', 'd': 'dragonfruit'}
    target = {'a': 'red', 'b': 'yellow', 'c': 'red', 'd': 'pink'}
    data_object = DataObject(data, target=target)

    # Equality operator
    assert data_object == {'a': 'apple', 'b': 'banana',
                           'c': 'cherry', 'd': 'dragonfruit'}
    # Inequality operator
    assert data_object != {'a': 'apple', 'b': 'banana',
                           'c': 'cherry', 'd': 'dingleberry'}
    # Inequality based on shape
    assert data_object != [{'a': 'apple', 'b': 'banana',
                            'c': 'cherry', 'd': 'dragonfruit'}]
    assert data_object != {'a': ['apple'], 'b': ['banana'],
                           'c': ['cherry'], 'd': ['dragonfruit']}

    # Iteration
    assert all(x in ['a', 'b', 'c', 'd'] for x in data_object)
    # Correct length
    assert len(data_object) == 4
    # Correct value construction
    assert data_object.value == {'a': 'apple', 'b': 'banana',
                                 'c': 'cherry', 'd': 'dragonfruit'}
    # Correct container construction
    assert data_object.container

    # Correct types
    assert isinstance(data_object.value, dict)
    assert all(isinstance(x, str) for x in data_object)
    assert all(isinstance(data_object[x], DataObject) for x in data_object)
    assert all(isinstance(data_object[x].value, str) for x in data_object)

    # Containment operator
    assert 'a' in data_object
    assert 'b' in data_object
    # Non-containment operator
    assert 'e' not in data_object
    assert 'f' not in data_object

    # String interpretation
    assert str(
        data_object) == "{'a': 'apple', 'b': 'banana', 'c': 'cherry', 'd': 'dragonfruit'}"
    # Representative interpretation
    assert repr(
        data_object) == "{'a': 'apple', 'b': 'banana', 'c': 'cherry', 'd': 'dragonfruit'}"

    # Correct property recursion
    assert data_object.target == {'a': 'red', 'b': 'yellow',
                                  'c': 'red', 'd': 'pink'}
    for key in data_object:
        assert data_object[key].target == data_object.target[key]

    # Get indexing integer
    assert data_object['a'] == 'apple'
    assert data_object['c'] == 'cherry'
    # Get indexing iterable
    assert data_object[['a', 'c', 'b']] == ['apple', 'cherry', 'banana']
    assert data_object[['b', 'd', 'b', 'c']] == ['banana', 'dragonfruit',
                                                 'banana', 'cherry']

    # Set indexing integer
    data_object['c'] = 'cranberry'
    assert data_object == {'a': 'apple', 'b': 'banana',
                           'c': 'cranberry', 'd': 'dragonfruit'}
    data_object['d'] = 'date'
    assert data_object == {'a': 'apple', 'b': 'banana',
                           'c': 'cranberry', 'd': 'date'}
    # Set indexing iterable
    data_object[['b', 'a']] = ['blueberry', 'apricot']
    assert data_object == {'a': 'apricot', 'b': 'blueberry',
                           'c': 'cranberry', 'd': 'date'}

    # Broadcasting to value
    assert data_object.keys
    assert data_object.values
    # Broadcasting to contained values
    assert data_object.lower
    assert data_object.upper


def test_container_pandas():
    """Test common functions of a container dataframe
    """

    # Create dict data object with corresponding target dict
    data = pd.DataFrame(np.arange(12).reshape(4, 3), columns=['z', 'x', 'y'])
    data_object = DataObject(data)

    # Equality operator
    assert data_object == {0: {'z': 0, 'x': 1, 'y': 2},
                           1: {'z': 3, 'x': 4, 'y': 5},
                           2: {'z': 6, 'x': 7, 'y': 8},
                           3: {'z': 9, 'x': 10, 'y': 11}}
    assert data_object == {0: {'z': [0], 'x': [1], 'y': [2]},
                           1: {'z': [3], 'x': [4], 'y': [5]},
                           2: {'z': [6], 'x': [7], 'y': [8]},
                           3: {'z': [9], 'x': [10], 'y': [11]}}
    # Inequality operator
    assert data_object != {0: {'z': 0, 'x': 1, 'y': 2},
                           1: {'z': 3, 'x': 4, 'y': 5},
                           2: {'z': 6, 'x': 7, 'y': 8},
                           3: {'z': 9, 'x': 10, 'y': 12}}
    # Inequality based on shape
    assert data_object != [{0: {'z': 0, 'x': 1, 'y': 2},
                            1: {'z': 3, 'x': 4, 'y': 5},
                            2: {'z': 6, 'x': 7, 'y': 8},
                            3: {'z': 9, 'x': 10, 'y': 11}}]

    # Iteration
    assert all(x in [0, 1, 2, 3] for x in data_object)
    # Correct length
    assert len(data_object) == 4
    # Correct value construction
    assert data_object.value == {0: {'z': 0, 'x': 1, 'y': 2},
                                 1: {'z': 3, 'x': 4, 'y': 5},
                                 2: {'z': 6, 'x': 7, 'y': 8},
                                 3: {'z': 9, 'x': 10, 'y': 11}}
    # Correct container construction
    assert data_object.container

    # # Correct types
    assert isinstance(data_object.value, dict)
    assert all(isinstance(x, int) for x in data_object)
    assert all(isinstance(data_object[x], DataObject) for x in data_object)
    assert all(isinstance(data_object[x].value, dict) for x in data_object)

    # Containment operator
    assert 0 in data_object
    assert 1 in data_object
    # Non-containment operator
    assert 5 not in data_object
    assert 6 not in data_object

    # Get indexing integer
    assert data_object[0] == {'z': 0, 'x': 1, 'y': 2}
    assert data_object[2] == {'z': 6, 'x': 7, 'y': 8}

    # Set indexing integer
    data_object[0]['x'] = 5
    assert data_object == {0: {'z': 0, 'x': 5, 'y': 2},
                           1: {'z': 3, 'x': 4, 'y': 5},
                           2: {'z': 6, 'x': 7, 'y': 8},
                           3: {'z': 9, 'x': 10, 'y': 11}}
    data_object[1]['z'] = 7
    assert data_object == {0: {'z': 0, 'x': 5, 'y': 2},
                           1: {'z': 7, 'x': 4, 'y': 5},
                           2: {'z': 6, 'x': 7, 'y': 8},
                           3: {'z': 9, 'x': 10, 'y': 11}}

    # Broadcasting to value
    assert data_object.keys
    assert data_object.values


def test_container_recursion_depth():
    """Test the recursion depth feature
    """

    # Create list data objects with different recursion depths specified
    data = [[[1, 2], [3, 4], [5, 6]], [[8, 9], [10, 11], [12, 13]]]
    data_object = DataObject(data)
    data_object_depth0 = DataObject(data, recursion_depth=0)
    data_object_depth1 = DataObject(data, recursion_depth=1)
    data_object_depth2 = DataObject(data, recursion_depth=2)

    # Check correct values
    assert data_object == data
    assert data_object_depth0 == data
    assert data_object_depth1 == data
    assert data_object_depth2 == data

    # Check default types
    assert isinstance(data_object[0], DataObject)
    assert isinstance(data_object[0][0], DataObject)
    assert isinstance(data_object[0][0][0], DataObject)

    # Check recursion_depth=0 types
    assert isinstance(data_object_depth0[0], list)
    assert isinstance(data_object_depth0[0][0], list)
    assert isinstance(data_object_depth0[0][0][0], int)

    # Check recursion_depth=1 types
    assert isinstance(data_object_depth1[0], DataObject)
    assert isinstance(data_object_depth1[0][0], list)
    assert isinstance(data_object_depth1[0][0][0], int)

    # Check recursion_depth=2 types
    assert isinstance(data_object_depth2[0], DataObject)
    assert isinstance(data_object_depth2[0][0], DataObject)
    assert isinstance(data_object_depth2[0][0][0], int)


def test_multi_index():
    """Test the multi-index feature
    """

    # Create a nested list data object
    data1 = [[[1, 2], [3, 4], [5, 6], [7, 8]],
             [[9, 10], [11, 12], [13, 14]]]
    target1 = [[[{'a': 14, 'b': 7}, {'a': 13, 'b': 8}],
                [{'a': 12, 'b': 6}, {'a': 11, 'b': 7}],
                [{'a': 10, 'b': 5}, {'a': 9, 'b': 6}],
                [{'a': 8, 'b': 4}, {'a': 7, 'b': 5}]],
               [[{'a': 6, 'b': 3}, {'a': 5, 'b': 4}],
                [{'a': 4, 'b': 2}, {'a': 3, 'b': 3}],
                [{'a': 2, 'b': 1}, {'a': 1, 'b': 2}]]]
    data_object1 = DataObject(data1)
    data_object1.target = target1

    # Get integer multi-index
    assert data_object1[0, 0, 0] == 1
    assert data_object1[1, 1, 1] == 12
    assert data_object1[0, 3, 1] == 8

    # Get list multi-index
    assert data_object1[0, [0, 2, 3], 0] == [1, 5, 7]
    assert data_object1[1, [0, 2], [1, 0]] == [[10, 9], [14, 13]]
    assert data_object1[[1, 0], 2, 1] == [14, 6]

    # Get range multi-index
    assert data_object1[0, 2:4, 0] == [5, 7]
    assert data_object1[:, 1::2, 1] == [[4, 8], [12]]
    assert data_object1[[1, 1, 0], :-3:-1, [0]] == [[[13], [11]], [[13], [11]], [[5], [7]]]

    # Get string multi-index
    assert data_object1.target[:, :, :] == [
        [[{'a': 14, 'b': 7}, {'a': 13, 'b': 8}],
         [{'a': 12, 'b': 6}, {'a': 11, 'b': 7}],
         [{'a': 10, 'b': 5}, {'a': 9, 'b': 6}],
         [{'a': 8, 'b': 4}, {'a': 7, 'b': 5}]],
        [[{'a': 6, 'b': 3}, {'a': 5, 'b': 4}],
         [{'a': 4, 'b': 2}, {'a': 3, 'b': 3}],
         [{'a': 2, 'b': 1}, {'a': 1, 'b': 2}]]]

    # Get string slice multi-index
    assert data_object1.target[:, :, :, 'a'] == [[[14, 13], [12, 11], [10, 9], [8, 7]],
                                                 [[6, 5], [4, 3], [2, 1]]]
    assert data_object1.target[:, :, :, 'b'] == [[[7, 8], [6, 7], [5, 6], [4, 5]],
                                                 [[3, 4], [2, 3], [1, 2]]]
    assert data_object1.target[0, [0, 3], 0, ['b', 'a']] == [[7, 14], [4, 8]]

    # Create nested dict/list data object
    data2 = {'a': ['apple', 'apricot'],
             'b': ['banana', 'blueberry', 'boysenberry']}
    data_object2 = DataObject(data2)

    # Get multi-indexing
    assert data_object2['a'] == ['apple', 'apricot']
    assert data_object2['a', 1] == 'apricot'
    assert data_object2[['b', 'a'], 0] == ['banana', 'apple']


def test_broadcast_access():
    """Test accessing a property of all contained items of a DataObject.
    """

    # Create data and views informatoin
    data = [1, 2, 3, 4]
    targets = {'target1': 0, 'target2': 3}
    views = {'alpha': ['a', 'b', 'c', 'd'], 'numeric': ['one', 'two', 'three', 'four']}

    # Encapsulate data into data object
    data_obj = DataObject(data, targets=targets, views=views)

    # Retrieve view named 'alpha' for all elements
    alpha_view = data_obj.views['alpha']
    numeric_view = data_obj.views['numeric']

    # Verify that views contain the correct values
    assert alpha_view == ['a', 'b', 'c', 'd']
    assert numeric_view == ['one', 'two', 'three', 'four']

    # Verify that targets contains the correct values
    assert data_obj.targets == {'target1': 0, 'target2': 3}

    # Verify that individual views contain correct values
    assert data_obj[0].views["alpha"] == "a"
    assert data_obj.views["alpha"][0] == "a"

def test_save_load_simple():
    """Test saving and loading a simple DataObject
    """

    path = os.path.expanduser('~/.ex4ml/tests/save/simple.json')

    n = 10
    my_views = [{
        "feats": [i**2, i**3, i**4],
        "basic": [i*2, i*3, i*4]
    } for i in range(n)]

    my_targets = [{
        "label": "A"
    } if i % 3 == 0 else {
        "label": "B"
    } for i in range(n)]

    my_do = DataObject(list(range(n)), views=my_views, targets=my_targets)

    my_do.save(path)

    loaded_do = DataObject.load_from(path)


def test_save_load_iris():
    """Test saving and loading a DataObject created from iris
    """

    data = load_iris()

    my_do = DataObject([DataObject(None, views={"feats": datum[0]}, targets={"species": datum[1]}) for datum in zip(data["data"], data["target"])])

    path = os.path.expanduser('~/.ex4ml/tests/save/iris.json')

    my_do.save(path)

    loaded_data = DataObject.load_from(path)
