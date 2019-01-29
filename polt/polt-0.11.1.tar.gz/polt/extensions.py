# system modules
import pkg_resources
import warnings
import logging

# internal modules
from polt.version import *
import polt.l10n
import polt.animator
import polt.streamer
import polt.parser
import polt.utils
import polt.config

# external modules

logger = logging.getLogger(__name__)


class EntryPointExtensions:
    """
    Class for detection of entry point extensions for :mod:`polt`
    """

    entry_point_subclasses = {
        POLT_PARSER_ENTRY_POINT: polt.parser.parser.Parser,
        POLT_ANIMATOR_ENTRY_POINT: polt.animator.Animator,
    }

    @classmethod
    def get(cls, name, subcls=None, aliases=False):
        """
        Check entry points. Invalid entry points are skipped with a warning.
        Entry points pointing to classes not inheriting from a given class are
        still included but with a warning.

        Args:
            name (str): the name of the entry point
            cls (class, optional): class to check inheritance for. Defaults to
                :class:`object`.
            aliases (bool, optional): Whether to pass the result through
                :meth:`aliases_from_entry_points` to determine the aliases.
                Default is ``False``.

        Returns:
            dict : mapping of :class:`pkg_resources.EntryPoint` s (if
            ``aliases`` is ``False``, tuples of unique alias strings otherwise)
            to the respective classes
        """
        if subcls is None:
            subcls = cls.entry_point_subclasses.get(name, object)
        entry_points = {}
        for entry_point in pkg_resources.iter_entry_points(name):
            try:
                entry_point_cls = entry_point.load()
            except BaseException as e:
                warnings.warn(
                    _(
                        "Could not load {entry_point} entry point {name} "
                        "from {dist}: {err}"
                    ).format(
                        entry_point=repr(name),
                        name=repr(entry_point.name),
                        err=e,
                        dist=repr(
                            entry_point.dist or _("unknown distribution")
                        ),
                    )
                )
                continue
            try:
                if not issubclass(entry_point_cls, subcls):
                    warnings.warn(
                        _(
                            "{entry_point} entry point named {name} "
                            "from {dist} points to class "
                            "{entry_point_cls} which is not a "
                            "{subcls} subclass "
                            "and thus might not work"
                        ).format(
                            entry_point=repr(name),
                            name=repr(entry_point.name),
                            entry_point_cls=entry_point_cls,
                            subcls=subcls,
                            dist=repr(
                                entry_point.dist or _("unknown distribution")
                            ),
                        )
                    )
            except BaseException as e:
                warnings.warn(
                    _(
                        "Skipping {entry_point} entry point named {name} "
                        "from {dist} pointing to {obj} which is "
                        "obviously not a type: {err}"
                    ).format(
                        entry_point=repr(subcls),
                        name=repr(entry_point.name),
                        obj=repr(entry_point_cls),
                        err=e,
                        dist=repr(
                            entry_point.dist or _("unknown distribution")
                        ),
                    )
                )
                continue
            matching_ep = next(
                filter(lambda ep: ep.name == entry_point.name, entry_points),
                None,
            )
            if matching_ep:
                warnings.warn(
                    _(
                        "{dist1} and {dist2} both define a {entry_point} "
                        "entry point {name}."
                    ).format(
                        dist1=repr(
                            matching_ep.dist or _("unknown distribution")
                        ),
                        dist2=repr(
                            entry_point.dist or _("unknown distribution")
                        ),
                        entry_point=repr(name),
                        name=repr(entry_point.name),
                    )
                )
            entry_points[entry_point] = entry_point_cls
        return (
            cls.aliases_from_entry_points(entry_points)
            if aliases
            else entry_points
        )

    @staticmethod
    def aliases_from_entry_points(entry_points):
        """
        Create mapping of aliases to classes from

        Args:
            entry_points (dict): mapping of entry points to the respective
                classes

        Returns:
            dict : mapping of tuples of unique alias strings to classes
        """
        final_aliases = {}
        for entry_point, final_cls in sorted(
            entry_points.items(),
            key=lambda x: (
                "0" if x[0].module_name.startswith("polt") else str(x[0])
            ),
        ):

            aliases = []
            full = (
                ".".join(filter(bool, (entry_point.module_name, a)))
                for a in entry_point.attrs
            )
            for alias in filter(
                bool,
                (entry_point.name,) + tuple(entry_point.attrs) + tuple(full),
            ):
                if any(alias in a for a in final_aliases):
                    continue
                aliases.append(alias)
            final_aliases[tuple(aliases)] = final_cls
        return final_aliases

    @staticmethod
    def short_aliases(aliases):
        """
        Generate a list of aliases

        Args:
            aliases (sequence of sequences): sequence of sequences with alias
                strings

        Returns:
            tuple : the first aliases
        """
        return tuple(
            map(
                repr,
                sorted(filter(bool, (next(iter(a), None) for a in aliases))),
            )
        )
