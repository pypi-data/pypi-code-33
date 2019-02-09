""" An abstract class representing output channel notifications."""
# Standard modules
import abc
import importlib
import inspect
import os


def outputs():
    """
    Return a list of all output classes.
    """
    outputs_ = {}
    here = os.path.abspath(os.path.dirname(__file__))

    # Get all packages from the output module
    for file_ in os.listdir(here):
        if file_[-3:] == '.py' and file_ != '__init__.py':
            name = file_[:-3]
            path = os.path.join(here, file_)

            # Directly import the file from output directory
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get the output class from the module
            _, output_class = inspect.getmembers(
                module, inspect.isclass)[0]
            # Add it to the list of possible outputs
            outputs_[name] = output_class
    return outputs_


class Output(abc.ABC):  # pylint: disable=too-few-public-methods
    """
    Represents output channel for notifications.

    Attributes:
        subject (str): Subject of notification.
        content (str): Content of notification.
        config (dict): Configuration options.
        only_url: True if it is not possible to send diffs through the channel.
    """
    only_url = False

    def __init__(self, subject, content, config):
        super(Output, self).__init__()
        self.subject = subject
        self.content = content
        self.config = config

    @abc.abstractmethod
    def send(self):
        """
        Sends notification.

        Returns:
            bool: True if notification was successful.
        """
        raise NotImplementedError
