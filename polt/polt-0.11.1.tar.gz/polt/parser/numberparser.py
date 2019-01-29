# system modules
import re
import logging

# internal modules
from polt.parser.parser import Parser

# external modules

logger = logging.getLogger(__name__)


class NumberParser(Parser):
    """
    Simple parser extracting numbers line-wise

    Args:
        f (file-like object, optional): the connection to read from
        name (str, optional): human-readable description of the parser
        quantity (str, optional): quantity of the numbers read
        unit (str, optional): unit of the numbers read
        key (str, optional): key of the numbers read
    """

    NUMBER_REGEX = re.compile(r"-?\d+(?:\.\d+)?")
    """
    Regular expression to detect numbers
    """

    def __init__(self, f=None, name=None, quantity=None, unit=None, key=None):
        Parser.__init__(self, f=f, name=name)
        if quantity is not None:
            self.quantity = quantity
        if unit is not None:
            self.unit = unit
        if key is not None:
            self.key = key

    @property
    def quantity(self):
        """
        The name of the quantity of the parsed numbers.

        .. note::

            Set this option from the command-line via
            ``polt add-source -p numbers -o quantity=NAME``

        """
        try:
            self._quantity
        except AttributeError:
            self._quantity = _("number")
        return self._quantity

    @quantity.setter
    def quantity(self, new):
        self._quantity = new

    @property
    def unit(self):
        """
        The unit of the parsed numbers.

        .. note::

            Set this option from the command-line via
            ``polt add-source -p numbers -o unit=UNIT``

        """
        try:
            self._unit
        except AttributeError:
            self._unit = None
        return self._unit

    @unit.setter
    def unit(self, new):
        self._unit = new

    @property
    def key(self):
        """
        The key of the parsed numbers.

        .. note::

            Set this option from the command-line via
            ``polt add-source -p numbers -o key=KEY``

        """
        try:
            self._key
        except AttributeError:
            self._key = None
        return self._key

    @key.setter
    def key(self, new):
        self._key = new

    @property
    def data(self):
        logger.debug(
            _("Reading from {}...").format(
                self.f.name if hasattr(self.f, "name") else repr(self.f)
            )
        )
        for line in self.f:
            if not line.strip():
                continue
            logger.debug(
                _("Received {} from {}").format(
                    repr(line),
                    self.f.name if hasattr(self.f, "name") else repr(self.f),
                )
            )
            numbers = (
                float(m.group())
                for m in self.NUMBER_REGEX.finditer(
                    line.decode(errors="ignore")
                    if hasattr(line, "decode")
                    else line
                )
            )
            numbers_list = list(numbers)
            logger.debug(_("Numbers extracted: {}").format(numbers_list))
            yield {(self.quantity, self.unit, self.key): numbers_list}
