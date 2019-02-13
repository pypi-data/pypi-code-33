from abc import abstractmethod
from .documentable import Documentable
import os
import shutil
import threading
import inspect
from .library import Library


class OperationException(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super(OperationException, self).__init__(message)


class Operation(Documentable):
    """This abstract class is the mother class for operations. An operation is a specific action on a JTracker workflow.
    Two methods have to be implemented for childen classes.
    _schema and _run"""

    def __init__(self, library=None, args=None, output=None, unknown_args=None):
        """
        Constructor of the Operation

        Params:
            library Library: The library where the operation is added
            args: Arguments added, normally from a parser
            output: The output of the operation
            unknown_args: Any other arguments provided
            observers: A list of observers to watch the operation
        """
        self.args = args
        self.output = output
        self.main_thread = None
        self.completed = False
        self.unknown_args = unknown_args
        self._library = library
        self._observers = []
        return

    def set_args(self, args):
        """
        Set the arguments required by the operation available at the operation entry with argparse.

        Args:
            args (dict): Dictionary of required arguments to run the operation
        """
        self.args = args
        return

    def set_unknown_args(self, args):
        """
        Set the unknown arguments by the operation available at the operation entry with argparse.
        Args:
            args (dict): Dictionary of arguments that are not in the known arguments
        :param args:
        :return:
        """
        self.unknown_args = args

    def get_args(self):
        """
        Return the args provided at the entry of the operation

        Return:
            dict: Arguments
        """
        return self.args

    def set_output(self, output):
        """
        Set the output attribute

        Args:
            output: The available output at the end of the operation
        """
        self.output = output
        return

    def get_output(self):
        """
        Return the output attribute

        Return:
            The output value
        """
        return self.output

    @abstractmethod
    def _schema(self):
        """
        Returns the validation schema for the config file needed to run the operation.

        Return:
            dict: A validation dictionary

        Raises:
            NotImplementedError: The method has not been implemented yet
        """
        raise NotImplementedError

    @abstractmethod
    def _run(self):
        """
        The logic of the operation. The config dictionary can be retrieved in the config dictionary: self._config

        Raises:
            NotImplementedError: The method has not been implemented yet
        """
        raise NotImplementedError

    def execute(self, args, unknown_args):
        """
        This method is the main one executed. It triggers all the hooks, before_start, on_running, on_error, on_completed.

        Args:
            args (dict): The required arguments to run the operation
        """
        self.set_args(args)
        self.set_unknown_args(unknown_args)

        run = self.before_start()
        if run:
            self.on_running()
            self.run()
            self.on_completed()
        return

    def run(self):
        """
        Main function that runs the operation
        """
        try:
            self.set_output(self._run())
            self.completed = True
        except Exception as err:
            self.completed = True
            self.on_error(err)
            exit(1)
        return

    def parser(self, main_parser):
        """
        Add all subparsers and parent subparsers to argparse

        Args:
            main_parser: Argparse parser
        """
        for cb in self.__class__.__bases__:
            if issubclass(cb, Operation):
                cb().parser(main_parser)
        self._parser(main_parser)
        return

    def _parser(self, main_parser):
        """
        Add parser to the main argparse parser

        Args:
            main_parser: Add parser to argparse parser
        """
        return

    @staticmethod
    def environ_or_required(key):
        """
        Return True if the key exists in the OS environment, False otherwise

        Args:

        :param key:
        :return:
        """
        if os.environ.get(key):
            return {'default': os.environ.get(key)}
        else:
            return {'required': True}

    def before_start(self):
        """
        This method is triggered right before executing the run. At this point, the arguments are already accessible
        in the class. This is the perfection function to establish some rules before running the operation. If those rules are
        not respected, return False and the operation is not going to be run. This method should not be overriden.

        Return:
            bool: False if the operation cannot be run, True otherwhise
        """
        for observer in self._observers:
            observer.before_start(self)
        return self._before_start()

    def _before_start(self):
        """
        This method is wrapped under before_start method to be overriden. This method contains the specific logic of an operation.
        Return:
            bool: False if the operation cannot be run, True otherwhise
        """
        return True

    def on_completed(self):
        """
        Once the operation is done, this hook is ran. This method should not be overriden.
        Return:
            bool: True if everything was done successfully, False otherwise
        """
        for observer in self._observers:
            observer.on_completed(self)
        return self._on_completed()

    def _on_completed(self):
        """
        This method is wrapped under on_completed to be overriden. This method contains the specific logic for an operation
        Return:
            bool: True if everything was done successfully, False otherwise
        """
        return True

    def on_running(self):
        """
        While the operation is running, this method is triggerred. In orther to change the invterval in second, this method is executed,
        the user can provide --TIMER {time_in_second}. This operation should not be overriden
        Return:
            bool: True if the operation should keep running, False otherwise
        """
        if not self.completed:
            threading_timer = threading.Timer(1, self.on_running)
            threading_timer.setDaemon(True)
            threading_timer.start()

        for observer in self._observers:
            observer.on_running(self)
        return self._on_running()

    def _on_running(self):
        """
        This method is wrapped under on_running method to be overriden. This method contains the specific logic on an operation
        Return:
            bool: True if the operation should keep running, False otherwise
        """
        return True

    def on_error(self, exception):
        """
        This method is triggered in case of an exception. This method should not be overriden.

        Parms:
            exception: The exception raised by the operation
        """
        for observer in self._observers:
            observer.on_error(exception, self, exception)
        return self._on_error(exception)

    def _on_error(self, exception):
        """
        This method is wrapped under on_error to be overriden. This method contains the specific logic for an operaion in case of an error.

        Raises:
            The operation exception raised by the operation while running.
        """
        raise Exception

    @classmethod
    def install(cls):
        """
        Install everything required to run the operation. This method should not be overriden.
        """
        requirements = os.path.dirname(inspect.getfile(cls)) + "/requirements.txt"
        if os.path.isfile(requirements):
            os.system('pip3 install -r %s' % requirements)
        return

    def is_publishable(self):
        """
        Return True if the operation publishes files, Falst otherwise

        Return:
            bool: True if the operation is publishable, False otherwise
        """
        return True


    def operation_dir(self):
        """
        Path of the operation directory

        Return:
            str: Path of the operation directory
        """
        return os.path.dirname(inspect.getfile(self.__class__))

    def resource_dir(self):
        """
        Path of the resource directory

        Return:
            str: Path of the default resource directory
        """
        return os.path.join(self.operation_dir(),"resources")

    def resource_file(self, filepath):
        """
        Retrieve a resource file

        Params:
            filepath: Path of the file in the operation resource directory

        Return:
            str: File path in the resource directory

        Raises:
            OperationException: The resource file does not exist in the operation directory
        """
        file = os.path.join(self.resource_dir(),filepath)
        if not os.path.isfile(file) and not os.path.isdir(file):
            raise OperationException("The resource file does not exist: %s" % (file))
        return os.path.join(self.resource_dir(),filepath)

    def publish(self, out_dir, path='.'):
        """
        Copy the operation resource files to the main resource directory

        Params:
            out_dir: Path of the output directory
        """
        shutil.copytree(self.resource_file(path), out_dir)
        return

    def get_library(self):
        """
        Return the library associated to the Operation

        Return:
            Library: The associated library
        """
        return self._library

    def add_observer(self, operation_observer):
        """
        Add an observer to the operation

        Params:
            operation_observer OperationObserver: An observer to register
        """
        self._observers.append(operation_observer)
        return

    def get_observers(self):
        """
        Return the list of registered observers
        """
        return self._observers
