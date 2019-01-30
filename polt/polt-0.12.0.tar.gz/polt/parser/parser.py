# system modules
import inspect
import logging

from abc import ABC, abstractproperty

# internal modules

# external modules

logger = logging.getLogger(__name__)


class Parser(ABC):
    """
    Abstract base class for parsers.

    Args:
        f (file-like object, optional): the connection to read from
        name (str, optional): human-readable description of the parser
    """

    def __init__(self, f=None, name=None):
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)[0]
        for arg in args[1:]:
            val = locals().get(arg)
            if val is not None:
                setattr(self, arg, val)

    @property
    def name(self):
        """
        Human-readable description of the parser

        :type: :class:`str`
        :getter: If no :attr:`name` was set yet, attempt to return a
            meaningful name based on :attr:`f`.
        """
        try:
            return self._name
        except AttributeError:
            return _("{} on {}").format(
                type(self).__name__,
                self.f.name if hasattr(self.f, "name") else repr(self.f),
            )

    @name.setter
    def name(self, new):
        self._name = str(new)

    @property
    def f(self):
        """
        The connection to read from
        """
        try:
            self._f
        except AttributeError:  # pragma: no cover
            self._f = None
        return self._f

    @f.setter
    def f(self, new):
        self._f = new

    @abstractproperty
    def data(self):
        """
        Generator yielding the next dataset. This is an
        :meth:`abc.abstractproperty`, thus subclasses have to override this.

        Yields:
            dict : dictionary like

                .. code:: python

                    {
                        quantity_spec1: value1,
                        quantity_spec2: value2,
                        quantity_spec3: value3,
                        ...
                    }

                quantity_spec
                    either a :class:`str` containing the name of the quantity
                    or a :class:`tuple` ``(name, unit, key)`` specifying the
                    quantity's name, unit and key
                value
                    either a single value or a sequence of values
        """
        pass
