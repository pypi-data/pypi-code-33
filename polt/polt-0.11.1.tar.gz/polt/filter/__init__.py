# system modules
import functools
import logging
from abc import ABC, abstractmethod

# internal modules

# external modules

logger = logging.getLogger(__name__)


class Filter(ABC):
    """
    The :class:`Filter` is a class to modify values before plotting them in the
    :any:`Animator`.
    """

    @property
    def when_parser(self):
        """
        Only operate on datasets from a given parser

        .. note::

            Set this option from the command-line via
            ``polt add-filter -o when-parser=PARSER``

        :type: :class:`str` or ``None``
        """
        try:
            self._when_parser
        except AttributeError:
            self._when_parser = None
        return self._when_parser

    @when_parser.setter
    def when_parser(self, new):
        self._when_parser = str(new) if new else None

    @staticmethod
    def chain(*filters):
        """
        Chain filters together

        Args:
            filters (sequence of callables, optional): filters to chain

        Returns:
            callable : function taking a value as argument and returning the
            result of applying all given filters in order
        """
        return functools.partial(functools.reduce, lambda d, f: f(d), filters)

    @abstractmethod
    def update_dataset(self, dataset):
        """
        Modify a given dataset

        Args:
            dataset (dict): the dataset to modify

        Returns:
            dict or None: the modified dataset. ``None`` can be used to
            indicate that the dataset was modified in-place.

        .. note::

            This is an :any:`abc.abstractmethod`, so subclasses have to
            override this
        """

    def __call__(self, dataset):
        """
        If the :any:`when_parser` condition is not met just return given
        dataset. Otherwise, call :any:`update_dataset` with the given dataset.
        If that results in ``None``, assume that :any:`update_dataset` modified
        the dataset in-place and return it. Otherwise, return the return value
        of :any:`update_dataset`.
        """
        if self.when_parser is not None:
            if dataset.get("parser") != self.when_parser:
                return dataset
        modified = self.update_dataset(dataset)
        return dataset if modified is None else modified
