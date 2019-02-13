
from .library import Library
from .operation import Operation

class Kernel:

    __instance = None

    @staticmethod
    def get_instance():
        """
        Return the Kernel instance

        Return:
            Kernel: The created or not instance of the Kernel
        """
        if Kernel.__instance == None:
            Kernel()
        return Kernel.__instance

    def __init__(self):
        if Kernel.__instance != None:
            raise Exception("This class is a singleton")
        else:
            Kernel.__instance = self
        self._libraries = {}
        self.args = {}
        return

    def set_libraries(self, libraries):
        """
        Set the libraries

        Params:
            libraries dict: Dictionary containing libraries with command line name as key and library object as value
        """
        self._libraries = libraries
        return

    def get_libraries(self):
        """
        Return the dictionary of libraries

        Return:
            dict: Dictionary containing libraries with command line name as key and library object as value
        """
        return self._libraries

    def set_observers(self, observers_dict):
        """
        Add observers to operations in the dictionary

        Params:
            observers_dict dict: Dictionary containing observers with operation class name as key and list observer class names as value
        """
        for library_key in self.get_libraries():
            operations = self.get_libraries()[library_key].operations()
            for operation_key in operations:
                for observer_key in observers_dict:
                    if isinstance(operations[operation_key],observer_key):
                        for observer in observers_dict[observer_key]:
                            operations[operation_key].add_observer(observer())
        return

    def find_operation(self, library, operation):
        """
        Find an operation by name

        Args:
            library (str): Name of the library
            operation (str): Name of the operation

        Return:
            Operation: The operation found
        """
        return self._libraries[library].find_operation(operation)

    def find_library(self, library_name):
        """
        Find a library by name

        Args:
            library_name str: Name of the library

        Return:
            Library: The requested library
        """
        return self.get_libraries()[library_name]