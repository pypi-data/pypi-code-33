# system modules
import functools
import collections
import itertools
import math
import logging
import inspect
import datetime
import operator
import re

# internal modules
from polt.animator import Animator

# external modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date

logger = logging.getLogger(__name__)


class SubPlotsAnimator(Animator):
    """
    Animator sorting recieved data into subplots

    Args:
        args, kwargs: further arguments handed to the :any:`Animator`
            constructor.
        subplots_for (str, optional): for which metadata property
            (``"parser"``, ``"quantity"``, ``"unit"``, ``"key"``) subplots
            should be created. The default is to not use subplots and display
            all data in a single plot.
        tight_layout (bool, optional): whether to use
            :func:`matplotlib.pyplot.tight_layout` or not. Default is ``True``.
    """

    def __init__(self, *args, subplots_for=None, tight_layout=None, **kwargs):
        Animator.__init__(self, *args, **kwargs)
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)[0]
        for arg in args[1:]:
            val = locals().get(arg)
            if val is not None:
                setattr(self, arg, val)

    def matching_axes(self, props={}):
        """
        Generator yielding the next axes matching certain data properties

        Args:
            props (dict, optional): dictionary of data properties
                with keys

                source
                    name of the data source
                quantity
                    name of the data quantity
                unit
                    data unit
                key
                    data key

        Yields:
            matplotlib.axes.Subplot : the next matching axes instance
        """
        for ax in self.figure.axes:
            if all(
                props.get(k) == v
                for k, v in (
                    ax.restrictions if hasattr(ax, "restrictions") else {}
                ).items()
            ):
                yield ax

    def optimal_row_col_grid(self, n=None, width=None, height=None):
        """
        Determine the optimal number of rows and columns to fit a specified
        number of subplots into the :attr:`figure`, taking its current
        height/width-ratio into account. The algorithm minimizes both deviation
        of the grid ratio from the figure ratio and the left-free space.

        Args:
            n (int, optional): the minimum number of plots to fit into the
                figure. The default is the current amount of subplots.
            width, height (float, optional): the figure dimensions. Defaults to
                the current figure dimensions.

        Returns:
            n_rows, n_cols: the optimal number of rows and columns
        """
        n = len(self.figure.axes) if n is None else n
        width = self.figure.get_size_inches()[0] if width is None else width
        height = self.figure.get_size_inches()[1] if height is None else height
        return min(
            filter(
                lambda rowcol: rowcol[0] * rowcol[1] >= n,
                itertools.product(range(1, n + 1), range(1, n + 1)),
            ),
            key=lambda rowcol: (
                functools.reduce(
                    lambda c1, c2: c1 * (1 + c2),
                    (
                        1,
                        # relative ratio difference (in linear angle domain)
                        abs(
                            (
                                math.atan(height / width)
                                - math.atan(rowcol[0] / rowcol[1])
                            )
                            / math.atan(height / width)
                        ),
                        # left-free space ratio
                        # This ratio is artificially increased (weighted)
                        # as it yields more intuitive layouts
                        2
                        * (rowcol[1] * rowcol[0] - n)
                        / (rowcol[1] * rowcol[0]),
                    ),
                )
            ),
        )

    def reorder_subplots(self, n=None):
        """
        Reorder subplots on :attr:`figure` according
        :meth:`optimal_row_col_grid`.

        After reordering the subplots, the registry hook
        ``"after-reordering-subplots"`` is executed.

        Args:
            n (int, optional): the minimum number of plots to fit onto the
                figure. The default is the current amount of subplots.

        Returns:
            n_rows, n_cols: the new number of rows and columns
        """
        rows, cols = self.optimal_row_col_grid(n=n)
        for i, ax in enumerate(self.figure.axes):
            ax.change_geometry(rows, cols, i + 1)
        self.call_registered_functions("after-reordering-subplots")
        return rows, cols

    def add_axes(self, restrictions={}, **kwargs):
        """
        Make room for a new subplot with :meth:`reorder_subplots` and add a
        new axes to the :attr:`figure`.

        After adding the axes, the registry hook ``"axes-added"`` is
        executed with the axes as argument.

        Args:
            restrictions (dict, optional): dictionary of restrictions for this
                axes with the following all-optional keys

                source
                    name of the data source
                quantity
                    name of the data quantity
                unit
                    data unit
                key
                    data key

                Only data with matching metadata will then be displayed on this
                axis. The default is no restriction.
            **kwargs: keyword arguments to
                :meth:`matplotlib.figure.Figure.add_subplot`

        Returns:
            matplotlib.axes.Subplot : the newly added axes
        """
        logger.debug(
            _("Creating new axes with restrictions {}").format(restrictions)
        )
        rows, cols = self.reorder_subplots(n=len(self.figure.axes) + 1)
        ax = self.figure.add_subplot(
            rows, cols, len(self.figure.axes) + 1, **kwargs
        )
        ax.restrictions = restrictions
        if ax.restrictions:
            ax.set_title(
                ", ".join(
                    (
                        {
                            "parser": _("no parser"),
                            "quantity": _("no quantity"),
                            "unit": _("no unit"),
                            "key": _("no key"),
                        }.get(prop, _("no {}").format(prop))
                        if val is None
                        else "{}: {}".format(
                            {
                                "parser": _("parser"),
                                "quantity": _("quantity"),
                                "unit": _("unit"),
                                "key": _("key"),
                            }.get(prop, prop),
                            val,
                        )
                    )
                    for prop, val in ax.restrictions.items()
                )
            )
        else:
            ax.set_title(_("Data from Every Parser, Quantity, Unit and Key"))
        self.call_registered_functions("axes-added", ax)
        return ax

    @property
    def tight_layout(self):
        """
        Whether to use :func:`matplotlib.pyplot.tight_layout` or not.

        .. note::

            Set this option from the command-line via
            ``polt live -a lines -o tight-layout=yes|no``


        :type: :class:`bool`
        """
        try:
            self._tight_layout
        except AttributeError:
            self._tight_layout = False
        return self._tight_layout

    @tight_layout.setter
    def tight_layout(self, new):
        self._tight_layout = (
            new == "yes" if isinstance(new, str) else bool(new)
        )

    @Animator.register_method("axes-added")
    def do_tight_layout(self, *args, **kwargs):
        """
        Auto-align the subplots with :any:`matplotlib.pyplot.tight_layout` if
        :any:`tight_layout` is ``True``.

        Args:
            args, kwargs: just accept further arguments that might come in from
                the registering
        """
        if self.tight_layout:
            plt.tight_layout()

    @Animator.register_method("key-pressed")
    def tight_layout_key_shortcut(self, event):
        """
        Callback to call :any:`do_tight_layout` if the pressed
        key was an ``t``.

        .. hint::

            This means, you can press ``t`` when using a
            :any:`SubPlotsAnimator` to improve the plot layout.

        Args:
            event (matplotlib.backend_bases.KeyEvent, optional): the key event
        """
        if event.key == "t":
            plt.tight_layout()

    @property
    def subplots_for(self):
        """
        For which metadata property (``"parser"``, ``"quantity"``, ``"unit"``,
        ``"key"``) subplots should be created. The default is to not use
        subplots and display all data in a single plot.

        .. note::

            Set this option from the command-line via
            ``polt live -a lines -o subplots-for=parser|quantity|unit|key``

        :type: :class:`str` or ``None``
        """
        try:
            self._subplots_for
        except AttributeError:
            self._subplots_for = None
        return self._subplots_for

    @subplots_for.setter
    def subplots_for(self, new):
        if new is None or new == "nothing":
            if hasattr(self, "_subplots_for"):
                del self._subplots_for
        else:
            self._subplots_for = str(new)
