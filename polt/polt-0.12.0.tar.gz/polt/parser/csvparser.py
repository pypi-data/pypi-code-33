# system modules
import re
import logging
import sys
import re
import functools
import itertools
import csv
import collections
import io


# internal modules
from polt.parser.parser import Parser
from polt.utils import str2num

# external modules

logger = logging.getLogger(__name__)


class CsvParser(Parser):
    """
    Parser for CSV input

    Args:
        f (file-like object, optional): the connection to read from
        name (str, optional): human-readable description of the parser
        header_regex (re.compile, optional): regular expression applied to the
            header to extract quantity and unit. See :attr:`header_regex` and
            :meth:`parse_header` for further information.
        only_columns (set of str, optional): only return columns in this
            set. The default is to use all columns without restriction.
        not_columns (set of str, optional): don't return columns in this
            set. This condition is stronger than ``only_columns``. The default
            is to use all columns without restriction.
        delimiter (str, optional): the delimiter to use. Default is a comma
            (``,``).
    """

    HEADER_REGEX_MATCHALL = re.compile(".*")
    """
    Default regular expression for :attr:`header_regex` matching everything.
    """

    HEADER_REGEX_UNIT_LAST = re.compile(
        pattern=r"(?P<quantity>.*?)(?:[^a-zA-Z0-9]+(?P<unit>[a-zA-Z0-9]+))?"
    )
    """
    Regular expression for use in :attr:`header_regex` or :meth:`parse_header`
    which extracts the unit as the last part of the header separated by a
    non-word character.
    """

    HEADER_REGEX_KEY_QUANTITY_UNIT = re.compile(
        pattern=r"(?P<key>[a-zA-Z0-9]+)"
        r"(?:"
        r"[^a-zA-Z0-9]+(?P<quantity>[a-zA-Z0-9]+)"
        r"(?:"
        r"[^a-zA-Z0-9]+(?P<unit>[a-zA-Z0-9]+)"
        r")?"
        r")?"
    )
    """
    Regular expression for use in :attr:`header_regex` or :meth:`parse_header`
    which extracts the key, then optionally the quantity and then optionally
    the unit from the header separated by a non-word character.
    """

    def __init__(
        self,
        f=None,
        name=None,
        header_regex=None,
        only_columns=None,
        not_columns=None,
        delimiter=None,
        **dictreader_kwargs
    ):
        Parser.__init__(self, f=f, name=name)
        self.dictreader_kwargs = dictreader_kwargs
        if header_regex is not None:
            self.header_regex = header_regex
        if only_columns is not None:
            self.only_columns = only_columns
        if not_columns is not None:
            self.not_columns = not_columns
        if delimiter is not None:
            self.delimiter = delimiter

    @property
    def header_regex(self):
        """
        Regular expression applied used as default in :meth:`parse_header`.
        Defaults to :attr:`HEADER_REGEX_MATCHALL`.

        :type: regular expression created with :meth:`re.compile`
        :setter: convert the given string to a pattern via :meth:`re.compile`.
            However, first it is tried to look for a class property from which
            the name looke similar to the given string. If a match is found,
            that regex is used. For example one could set :attr:`header_regex`
            to ``"unit-last"`` and :attr:`HEADER_REGEX_UNIT_LAST` would be
            used.
        """
        try:
            self._header_regex
        except AttributeError:
            self._header_regex = self.HEADER_REGEX_MATCHALL
        return self._header_regex

    @header_regex.setter
    def header_regex(self, new):
        if isinstance(new, str):
            for attr, value in self.__class__.__dict__.items():
                m = re.fullmatch(r"HEADER_REGEX_(\w+)", attr)
                if not m:
                    continue
                key = next(iter(m.groups()), None)
                if not key:
                    continue
                if (
                    key.lower().strip()
                    == re.sub(r"\W+", "_", new).lower().strip()
                ):
                    self._header_regex = value
                    return
        self._header_regex = re.compile(pattern=new)

    def modifies_csvreader(decorated_function):
        """
        Decorator for methods that require a reset of the :attr:`csvreader`
        """

        @functools.wraps(decorated_function)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "_csvreader"):
                logger.debug(
                    _("Resetting csvreader before {}").format(
                        decorated_function
                    )
                )
                del self._csvreader  # pragma: no cover
            return decorated_function(self, *args, **kwargs)

        return wrapper

    @property
    def csvreader(self):
        """
        The underlying csv parser

        :type: :class:`csv.DictReader`
        """
        try:
            self._csvreader
        except AttributeError:
            self._csvreader = csv.DictReader(self.f, **self.dictreader_kwargs)
        return self._csvreader

    @property
    def dictreader_kwargs(self):
        """
        Further keyword arguments for the underlying :attr:`csvreader`

        :type: :class:`dict`
        :setter: resets the :attr:`csvreader`
        """
        try:
            self._dictreader_kwargs
        except AttributeError:  # pragma: no cover
            self._dictreader_kwargs = {}
        return self._dictreader_kwargs

    @dictreader_kwargs.setter
    @modifies_csvreader
    def dictreader_kwargs(self, new):
        self._dictreader_kwargs = new

    @Parser.f.setter
    @modifies_csvreader
    def f(self, new):
        if hasattr(new, "mode"):
            if "b" in new.mode:
                logger.debug(
                    _(
                        "csv.DictReader cannot handle bytes input, "
                        "using utf-8 wrappter"
                    )
                )
                new = io.TextIOWrapper(new, "utf-8")
        self._f = new

    @property
    def only_columns(self):
        """
        Only yield these columns in :attr:`data`. The default is to use all
        columns.

        .. note::

            Set this option from the command-line via
            ``polt add-source -p csv -o only-columns=column1,column2,...``

        :type: :class:`set`
        :setter: splits string inputs by commas and converts input to
            :class:`set`
        """
        try:
            self._only_columns
        except AttributeError:
            self._only_columns = None
        return self._only_columns

    @only_columns.setter
    def only_columns(self, new):
        self._only_columns = set(
            new.split(",") if hasattr(new, "split") else new
        )

    @property
    def not_columns(self):
        """
        Don't yield these columns in :attr:`data`. This condition is stronger
        than :attr:`only_columns`. The default is to use all columns.

        .. note::

            Set this option from the command-line via
            ``polt add-source -p csv -o not-columns=column1,column2,...``

        :type: :class:`set`
        :setter: splits string inputs by commas and converts input to
            :class:`set`
        """
        try:
            self._not_columns
        except AttributeError:
            self._not_columns = set()
        return self._not_columns

    @not_columns.setter
    def not_columns(self, new):
        self._not_columns = set(
            new.split(",") if hasattr(new, "split") else new
        )

    @property
    def delimiter(self):
        """
        Delimiter to use. This is a convenience property to allow for
        simple setup via the command-line and configuration.

        .. note::

            Set this option from the command-line via
            ``polt add-source -p csv -o delimiter=DELIMITER``

        :type: :class:`str`
        :getter: returns the ``delimiter`` from :attr:`dictreader_kwargs`
        :setter: sets the ``delimiter`` (remove if ``None``) and sets
            :attr:`dictreader_kwargs`
        """
        return self.dictreader_kwargs.get("delimiter")

    @delimiter.setter
    @modifies_csvreader
    def delimiter(self, new):
        d = self.dictreader_kwargs
        if new is None:
            d.pop("delimiter", None)
        else:
            d.update(delimiter=str(new))
        self.dictreader_kwargs = d

    def str2num(self, s):
        """
        Convert a string or a sequence of strings to numbers with
        :meth:`polt.utils.str2num`.

        Args:
            s (str or sequence of str): the string(s) to convert

        Returns:
            (sequence of) str or int or float: the result of
                :meth:`polt.utils.str2num`
        """
        if isinstance(s, str):
            return str2num(s)
        elif isinstance(s, collections.Sequence):
            return [self.str2num(x) for x in s]
        else:
            return s

    def parse_header(self, header, regex=None):
        """
        Parse a header field name based on :attr:`header_regex` to determine
        its quantity name, unit and key. The quantity is extracted as either
        the content of the ``quantity`` named captured group or the first
        captured group with a fallback to the given header name itself. The
        unit is extracted similarly as either the content of the ``unit`` named
        captured group or the next captured group. The same for the key. By
        default, the unit and key are both ``None``.

        Args:
            header (str): the header field name
            regex (re.compile, optional): the regular expression to use.
                Default is :attr:`header_regex`.

        Returns:
            quantity, unit, key: quantity, unit and key
        """
        m = (regex if regex is not None else self.header_regex).fullmatch(
            header
        )
        quantity = header
        unit = None
        key = None
        if m:
            sources = list(m.groups())
            d = m.groupdict().copy()
            for p in ("quantity", "unit", "key"):
                val = d.get(p)
                if val in sources:
                    sources.remove(val)
                if p not in d:
                    if sources:
                        v = sources.pop(0)
                        if v is not None:
                            d.setdefault(p, v)
            d.setdefault("quantity", header)
            quantity = d.get("quantity")
            unit = d.get("unit")
            key = d.get("key")
        return quantity, unit, key

    @property
    def data(self):
        for row in self.csvreader:
            d = {
                self.parse_header(k): self.str2num(v)
                for k, v in row.items()
                if (
                    k is not None
                    and k
                    in (
                        self.only_columns
                        if self.only_columns is not None
                        else set(row)
                    )
                    - self.not_columns
                )
            }
            if d:
                yield d
