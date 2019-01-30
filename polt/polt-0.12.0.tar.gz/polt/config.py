# system modules
import configparser
import itertools
import subprocess
import inspect
import importlib
import logging
import shlex
import os
import re
import io
import sys

# internal modules
import polt
from polt.utils import normalize_cmd

# external modules
import xdgspec

USER_CONFIG_FILE = os.path.join(
    xdgspec.XDGPackageDirectory("XDG_CONFIG_HOME", "polt").path, "polt.conf"
)
LOCAL_CONFIG_FILE = ".polt.conf"

DEFAULT_CONFIG_FILES = (USER_CONFIG_FILE, LOCAL_CONFIG_FILE)

logger = logging.getLogger(__name__)


class SourceSectionError(ValueError):
    """
    Exception raised when the format of a :any:`Configuration.source_section`
    is invalid.
    """


class FilterSectionError(ValueError):
    """
    Exception raised when the format of a :any:`Configuration.filter_section`
    is invalid.
    """


class PlotSectionError(ValueError):
    """
    Exception raised when the format of the plot section is invalid.
    """


class Configuration(configparser.ConfigParser):
    """
    Class for configurations.
    """

    SOURCE_SECTION_PREFIX = "source"
    """
    Prefix for sections specifying a source
    """

    FILTER_SECTION_PREFIX = "filter"
    """
    Prefix for sections specifying a filter
    """

    @property
    def source_section(self):
        """
        Generator yielding source sections

        Yields:
            configparser.SectionProxy: the next source section
        """
        for name, section in self.items():
            if name.startswith(self.SOURCE_SECTION_PREFIX):
                yield section

    @property
    def filter_section(self):
        """
        Generator yielding filter sections

        Yields:
            configparser.SectionProxy: the next filter section
        """
        for name, section in self.items():
            if name.startswith(self.FILTER_SECTION_PREFIX):
                yield section

    def matching_source_section(self, command=None, parser=None):
        """
        Generator yielding source sections with a similar specification

        Args:
            cmd (str, optional): the command to check for
            parser (str, optional): the parser to check for

        Yields:
            configparser.SectionProxy: the next matching source section
        """
        for section in self.source_section:
            command_matches = False
            if command is not None:
                this_cmd = section.get("command")
                if not this_cmd:  # pragma: no cover
                    continue
                if normalize_cmd(this_cmd) == normalize_cmd(command):
                    command_matches = True
            else:
                command_matches = True
            parser_matches = False
            if parser is not None:
                this_parser = section.get("parser")
                parser_matches = this_parser == parser
            else:
                parser_matches = True
            if command_matches and parser_matches:
                yield section

    @staticmethod
    def to_string(value):
        """
        Convert a value to a sensible configuration string. :class:`bool`
        objects are converted to ``"yes"`` and ``"no"``, :class:`str` objects
        are left as they are and the rest is converted to :class:`str`.

        Args:
            value (object): the value to convert

        Returns:
            str : the converted string value
        """
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return "yes" if value else "no"
        return str(value)

    def add_section(self, name):
        """
        Add a new section with :any:`configparser.ConfigParser.add_section` but
        but if the name already exists, append something so that it doesn't
        exist.

        Args:
            name (str): the name of the new section

        Returns:
            str : the name actually used for the new section
        """
        nonexistant_name = next(
            filter(
                lambda x: x not in self,
                itertools.chain(
                    (name,),
                    (
                        " ".join(map(str, (name, _("nr."), nr)))
                        for nr in itertools.count(2)
                    ),
                ),
            )
        )
        configparser.ConfigParser.add_section(self, nonexistant_name)
        return nonexistant_name

    def update_option(self, section, key, value=None, default=None):
        """
        Update an option value

        Args:
            section (str): the name of the section
            key (str): the key
            value (object, optional): the new value. If ``None`` (the default)
                the value is left untouched or set to the value of ``default``
                if it is defined and the ``key`` doesn't exist.
                Is converted with :meth:`to_string`.
            default (object, optional): default fallback value if ``value`` is
                ``None``. Is converted with :meth:`to_string`.
        """
        if section not in self:
            self.add_section(section)
        sec = self[section]
        if value is None:
            if default is not None:
                if key not in sec:
                    sec[key] = self.to_string(default)
        else:
            sec[key] = self.to_string(value)

    def section_to_filter(self, section):
        """
        Set up a :any:`Filter` from a given section.

        Args:
            section (configparser.SectionProxy): the filter section

        Returns:
            parser.filter.Filter: the filter

        Raises:
            FilterSectionError : if the section format is wrong
        """
        filter_spec = section.get("filter")
        if filter_spec is None:
            raise FilterSectionError(
                _("Section {section} does not specify a 'filter'").format(
                    section=repr(section.name)
                )
            )
        parts = filter_spec.split(".")
        try:
            package, classname = ".".join(parts[:-1]), parts[-1]
            module = importlib.import_module(package)
            filter_cls = getattr(module, classname)
        except (IndexError, ImportError, AttributeError):
            raise SourceSectionError(
                _(
                    "filter specification {filter_spec} in "
                    "section {section} is not "
                    "an importable object"
                ).format(
                    filter_spec=repr(filter_spec), section=repr(section.name)
                )
            )
        if isinstance(filter_cls, type):
            if not issubclass(filter_cls, polt.filter.Filter):
                logger.warning(
                    _(
                        "Specified filter class {spec_class} is not a "
                        "subclass of {filter_class} and might not work."
                    ).format(
                        spec_class=filter_cls, filter_class=polt.filter.Filter
                    )
                )
            try:
                filter_obj = filter_cls()
            except BaseException as e:
                raise FilterSectionError(
                    _(
                        "Could not instantiate filter class {cls} from "
                        "section {section}: {err}"
                    ).format(
                        section=repr(section.name),
                        cls=repr(
                            ".".join(
                                (filter_cls.__module__, filter_cls.__name__)
                            )
                        ),
                        err=e,
                    )
                )
        else:
            filter_obj = filter_cls
        # set filter properties
        configured_filter_properties = {
            re.sub(r"\W+", "_", k.split(".")[1]): v
            for k, v in section.items()
            if (k.startswith("filter.") and k.split(".")[1])
        }
        for prop, val in configured_filter_properties.items():
            try:
                logger.debug(
                    _("Setting {filter}.{prop} to {val}").format(
                        prop=repr(prop), val=repr(val), filter=repr(filter_obj)
                    )
                )
                setattr(filter_obj, prop, val)
            except BaseException as e:
                logger.warning(
                    _(
                        "Could not set attribute {prop} to {val} "
                        "on filter {filter}: {err}"
                    ).format(
                        prop=repr(prop),
                        val=repr(val),
                        filter=repr(filter_obj),
                        err=repr(e),
                    )
                )
        if not hasattr(filter_obj, "__call__"):
            raise FilterSectionError(
                _("Filter object {filter} is not callable").format(
                    filter=filter_obj
                )
            )
        try:
            filter_obj({})
        except BaseException as e:
            raise FilterSectionError(
                _(
                    "Filter object {filter} can't modify an empty dataset: "
                    "{err}"
                ).format(filter=filter_obj, err=e)
            )
        return filter_obj

    def section_to_streamer(self, section):
        """
        Set up a :any:`Streamer` and :any:`Parser` from a given section. If the
        section defines a ``cmd``, that command will be launched with
        :class:`subprocess.Popen` and its :attr:`subprocess.Popen.stdout` will
        be used as :any:`Parser.f` input. Without ``cmd`` or if ``cmd`` is a
        dash (``-``), :attr:`sys.stdin` is used.

        Args:
            section (configparser.SectionProxy): the source section

        Returns:
            parser.streamer.Streamer: the set-up streamer with the set-up
                parser

        Raises:
            SourceSectionError : if the section format is wrong
        """
        parser_spec = section.get("parser")
        if parser_spec is None:
            raise SourceSectionError(
                _("Section {section} does not specify a 'parser'").format(
                    repr(section=section.name)
                )
            )
        parts = parser_spec.split(".")
        try:
            package, classname = ".".join(parts[:-1]), parts[-1]
            module = importlib.import_module(package)
            parser_cls = getattr(module, classname)
        except (IndexError, ImportError, AttributeError):
            raise SourceSectionError(
                _(
                    "parser specification {parser_spec} in "
                    "section {section} is not "
                    "an importable class specification"
                ).format(
                    parser_spec=repr(parser_spec), section=repr(section.name)
                )
            )
        if not issubclass(parser_cls, polt.parser.parser.Parser):
            logger.warning(
                _(
                    "Specified parser class {spec_class} is not a subclass "
                    "of {parser_class} and might not work."
                ).format(
                    spec_class=parser_cls,
                    parser_class=polt.parser.parser.Parser,
                )
            )
        cmd = section.get("command")
        encoding = section.get("encoding")
        if cmd:
            if cmd == "-":  # stdin
                if encoding:
                    try:
                        f = io.TextIOWrapper(
                            sys.stdin.buffer,
                            encoding=encoding,
                            errors="ignore",
                        )
                    except BaseException as e:
                        logger.error(
                            _(
                                "Could not use given encoding {encoding}: "
                                "{err}. Continuing without changing encoding."
                            ).format(encoding=repr(encoding), err=e)
                        )
                        f = sys.stdin
                else:
                    f = sys.stdin
            else:  # a command
                try:
                    process = subprocess.Popen(
                        shlex.split(cmd),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                    )
                except BaseException as e:
                    raise SourceSectionError(
                        _("Could not start command {cmd}: {err}").format(
                            cmd=repr(cmd), err=e
                        )
                    )
                try:
                    returncode = process.wait(timeout=0.5)
                    if returncode == 0:
                        logger.warning(
                            _("Command {cmd} is already done").format(
                                cmd=repr(cmd)
                            )
                        )
                    else:
                        raise SourceSectionError(
                            _(
                                "Running {cmd} did not work "
                                "(return code {code})"
                            ).format(cmd=repr(cmd), code=returncode)
                        )
                except subprocess.TimeoutExpired:  # still running
                    logger.info(_("Successfully started {}").format(repr(cmd)))
                if encoding:
                    try:
                        # for backwards-compatibility with Python < 3.6 we
                        # can't just use the encoding and errors arguments of
                        # Popen().  Instead, we use an io.TextIOWrapper here.
                        f = io.TextIOWrapper(
                            process.stdout, encoding=encoding, errors="ignore"
                        )
                    except BaseException as e:
                        logger.error(
                            _(
                                "Could not use encoding {encoding} "
                                "for output of {cmd}: {err}"
                            ).format(
                                encoding=repr(encoding), cmd=repr(cmd), err=e
                            )
                        )
                        f = process.stdout
                else:
                    f = process.stdout
        else:
            raise SourceSectionError(
                _("Section {} does not specify a 'command'").format(
                    repr(section.name)
                )
            )
        source_text = _("stdin") if cmd == "-" else repr(cmd)
        parser_name = section.get("name") or _("{parser} on {source}").format(
            parser=parser_spec,
            source={"stdin": _("standard input")}.get(
                source_text, source_text
            ),
        )
        # create up parser
        try:
            parser = parser_cls(f)
        except BaseException as e:
            raise SourceSectionError(
                _(
                    "Could not instantiate parser {name} "
                    "with class {cls}: {err}"
                ).format(
                    name=repr(parser_name),
                    cls=repr(
                        ".".join((parser_cls.__module__, parser_cls.__name__))
                    ),
                    err=e,
                )
            )
        # set parser properties
        configured_parser_properties = {
            re.sub(r"\W+", "_", k.split(".")[1]): v
            for k, v in section.items()
            if (k.startswith("parser.") and k.split(".")[1])
        }
        for prop, val in configured_parser_properties.items():
            try:
                logger.debug(
                    _("Setting {parser}.{prop} to {val}").format(
                        prop=repr(prop), val=repr(val), parser=repr(parser)
                    )
                )
                setattr(parser, prop, val)
            except BaseException as e:
                logger.warning(
                    _(
                        "Could not set attribute {prop} to {val} "
                        "on parser {parser}: {err}"
                    ).format(
                        prop=repr(prop),
                        val=repr(val),
                        parser=repr(parser),
                        err=repr(e),
                    )
                )
        # create the streamer
        try:
            streamer = polt.streamer.Streamer(parser=parser)
        except BaseException as e:
            raise SourceSectionError(
                _(
                    "Could not instantiate the streamer for parser "
                    "{parser}: {err}"
                ).format(err=e, parser=parser.name)
            )
        # set streamer properties
        configured_streamer_properties = {
            re.sub(r"\W+", "_", k.split(".")[1]): v
            for k, v in section.items()
            if (k.startswith("streamer.") and k.split(".")[1])
        }
        for prop, val in configured_streamer_properties.items():
            try:
                logger.debug(
                    _("Setting {streamer}.{prop} to {val}").format(
                        prop=repr(prop), val=repr(val), streamer=repr(streamer)
                    )
                )
                setattr(streamer, prop, val)
            except BaseException as e:
                logger.warning(
                    _(
                        "Could not set attribute {prop} to {val} "
                        "on streamer {streamer}: {err}"
                    ).format(
                        prop=repr(prop),
                        val=repr(val),
                        streamer=repr(streamer),
                        err=repr(e),
                    )
                )
        return streamer

    @property
    def streamer(self):
        """
        Generator yielding :any:`Streamer` instances of all
        sections yielded from :any:`source_section` created with
        :any:`section_to_streamer`.
        """
        return map(self.section_to_streamer, self.source_section)

    @property
    def filter(self):
        """
        Generator yielding :any:`Filter` instances of all sections yielded from
        :any:`filter_section` created with :any:`section_to_filter`.
        """
        return map(self.section_to_filter, self.filter_section)

    @property
    def animator(self):
        """
        Create an animator from the configuration.
        """
        self.update_option("plot", "animator")
        section = self["plot"]
        animator_spec = section.get("animator")
        if not animator_spec:
            raise PlotSectionError(
                _("plot section does not contain an 'animator'")
            )
        parts = animator_spec.split(".")
        try:
            package, classname = ".".join(parts[:-1]), parts[-1]
            module = importlib.import_module(package)
            animator_cls = getattr(module, classname)
        except (IndexError, ImportError, AttributeError):
            raise PlotSectionError(
                _(
                    "animator specification {animator_spec} is not "
                    "an importable class specification"
                ).format(animator_spec=repr(animator_spec))
            )
        if not issubclass(animator_cls, polt.animator.Animator):
            logger.warning(
                _(
                    "Specified animator class {spec_class} "
                    "is not a subclass "
                    "of {animator_class} and might not work."
                ).format(
                    spec_class=animator_cls,
                    animator_class=polt.animator.Animator,
                )
            )
        try:
            animator = animator_cls()
        except BaseException as e:
            raise PlotSectionError(
                _(
                    "Could not instantiate animator " "with class {cls}: {err}"
                ).format(
                    cls=repr(
                        ".".join(
                            (animator_cls.__module__, animator_cls.__name__)
                        )
                    ),
                    err=e,
                )
            )
        # set animator properties
        configured_animator_properties = {
            re.sub(r"\W+", "_", k.split(".")[1]): v
            for k, v in section.items()
            if (k.startswith("animator.") and k.split(".")[1])
        }
        for prop, val in configured_animator_properties.items():
            try:
                logger.debug(
                    _("Setting {animator}.{prop} to {val}").format(
                        prop=repr(prop), val=repr(val), animator=repr(animator)
                    )
                )
                setattr(animator, prop, val)
            except BaseException as e:
                logger.warning(
                    _(
                        "Could not set attribute {prop} to {val} "
                        "on animator {animator}: {err}"
                    ).format(
                        prop=repr(prop),
                        val=repr(val),
                        animator=repr(animator),
                        err=repr(e),
                    )
                )
        return animator
