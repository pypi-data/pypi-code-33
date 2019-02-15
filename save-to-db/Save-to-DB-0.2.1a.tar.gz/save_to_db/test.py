import inspect
from save_to_db import tests
from unittest import TestCase


def load(storage):
    # loading all tests into current name space
    for test_class_name, test_class in inspect.getmembers(tests):
        if not inspect.isclass(test_class) or not issubclass(test_class, TestCase):
            continue
        
        storage[test_class_name] = test_class
        

