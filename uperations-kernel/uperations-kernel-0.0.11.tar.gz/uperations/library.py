
from .documentable import Documentable
import inspect
import os
from abc import abstractmethod


class Library(Documentable):
    def __init__(self, slug=None):
        self._slug = slug
        self._operations = {}
        self._init_operations()
        return

    @abstractmethod
    def _init_operations(self):
        raise NotImplementedError

    @abstractmethod
    def operations(self):
        """
        Return a directory containing the list of operations
        :return:
        """
        return self._operations

    def set_slug(self, slug):
        """
        Assign a slug to the library

        Param:
            slug str: The slug to be assigned
        """
        self._slug = slug
        return

    def get_slug(self):
        """
        Return the library's slug

        Return:
            str: Library's slug
        """
        return self._slug

    def library_dir(self):
        """
        Return the directory path of the library

        Return:
            str: The path of the library directory in the project
        """
        return os.path.dirname(inspect.getfile(self.__class__))

    def operations_dir(self):
        return os.path.join(self.library_dir(),'operations')

    def observers_dir(self):
        return os.path.join(self.library_dir(),'observers')

    def operation_types_dir(self):
        return os.path.join(self.library_dir(),'operation_types')

    def find_operation(self, operation_name):
        return self.operations()[operation_name]