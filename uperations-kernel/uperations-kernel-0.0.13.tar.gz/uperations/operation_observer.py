
import abc

class OperationObserver:

    """
    An Operation Observer is based on the Observer pattern. An Operation has a life cycle and triggers
    methods at every steps of the life cycle. Once those methods are triggered, the observers are directly advised.
    The purpose of the observer is to be able to perform some actions without modifying the operation content.
    You can create has many observers as you want, they only need to be registered in the list of observers
    of the operation.
    """

    def before_start(self, operation, args=None):
        """
        Triggered before the function starts running. This is the wrapper of the core function
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        """
        self._before_start(operation, args)
        return

    @abc.abstractmethod
    def _before_start(self, operation, args=None):
        """
        Triggered before the function starts running
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        """
        return

    def on_running(self, operation, args=None):
        """
        Triggered while the operation is running. This is the wrapper of the core function
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        """
        self._on_running(operation, args)
        pass

    @abc.abstractmethod
    def _on_running(self, operation, args=None):
        """
        Triggered while the operation is running
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        """
        pass

    def on_completed(self, operation, args=None):
        """
        Triggered when the operation is completed. This is the wrapper of the core function
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        """
        self._on_completed(operation, args)
        pass

    @abc.abstractmethod
    def _on_completed(self, operation, args=None):
        """
        Triggered when the operation is completed.
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        """
        pass

    @abc.abstractmethod
    def _on_error(self, operation, err, args):
        """
        Triggered when the operation has an error.
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        :param err: The error triggered
        """
        pass

    def on_error(self, operation, err, args):
        """
        Triggered when the operation has an error. This is the wrapper of the core function
        :param operation Operation: The operation triggering the method
        :param args: Other arguments provided by the operation
        :param err: The error triggered
        """
        self._on_error(operation, err, args)
        pass