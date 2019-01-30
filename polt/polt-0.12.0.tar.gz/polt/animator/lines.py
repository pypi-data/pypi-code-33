# system modules
import functools
import collections
import itertools
import logging
import inspect
import datetime
import operator
import re
from abc import abstractmethod

# internal modules
from polt.animator.subplots import SubPlotsAnimator
from polt.utils import *

# external modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date

logger = logging.getLogger(__name__)


class LinesAnimator(SubPlotsAnimator):
    """
    Animator to display recieved data as lines.

    Args:
        args, kwargs: further arguments handed to the
            :any:`SubPlotsAnimator` constructor.
    """

    @property
    def only_expand_view(self):
        """
        Whether to always expand the view. Default is ``False``.

        .. note::

            Set this option from the command-line via
            ``polt live -o only-expand-view=yes|no``

        :type: :class:`bool`
        """
        try:
            self._only_expand_view
        except AttributeError:
            self._only_expand_view = False
        return self._only_expand_view

    @only_expand_view.setter
    def only_expand_view(self, new):
        self._only_expand_view = (
            new == "yes" if isinstance(new, str) else bool(new)
        )

    def matching_line(self, props={}, ax=None):
        """
        Generator yielding the next line matching a data properties

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

            ax(matplotlib.axes.Subplot, optional): the axes to look on.
                Defaults to all axes on :attr:`figure`.

        Yields:
            matplotlib.lines.Lines2D : the next matching line instance
        """
        for cur_ax in self.matching_axes(props) if ax is None else [ax]:
            for line in cur_ax.get_lines():
                if all(
                    props.get(k) == v
                    for k, v in (
                        line.restrictions
                        if hasattr(line, "restrictions")
                        else {}
                    ).items()
                ):
                    yield line

    @abstractmethod
    def new_line_coords(self, values, dataset={}):
        """
        Given values, determine coordinates for a new line.

        .. note::

            This is an :func:`abc.abstractmethod`, so subclasses have to
            override this.

        Args:
            values (sequence of float): the values to use
            dataset (dict, optional): the whole dataset where the values were
                extracted from. This is a dataset from :any:`Animator.buffer`
                as appended by :any:`Streamer.run`. The default is an empty
                dictionary.

        Returns:
            x, y, kwargs, attrs: ``x`` and ``y`` are coordinates as something
            that can be used for :any:`matplotlib.lines.Line2D.set_xdata` and
            :any:`matplotlib.lines.Line2D.set_ydata`. ``kwargs`` is a
            dictionary with further keyword arguments to
            :any:`matplotlib.axes.Axes.plot`. ``attrs`` is a dictionary of
            attributes and values which should be set on the newly created
            line.
        """

    @abstractmethod
    def update_line(self, line, values, dataset={}):
        """
        Update a given line with values

        .. note::

            This is an :func:`abc.abstractmethod`, so subclasses have to
            override this.

        Args:
            line (matplotlib.lines.Line2D): the line to update
            values (sequence of float): the values to use for updating
            dataset (dict, optional): the whole dataset where the values were
                extracted from. This is a dataset from :any:`Animator.buffer`
                as appended by :any:`Streamer.run`. The default is an empty
                dictionary.
        """

    def update_figure_with_dataset(self, dataset):
        """
        Update the figure with a single dataset.

        The following registry hooks are executed:

        matching-axes-found
            When the axes for the line was determined this hook is executed and
            handed the axes as ``ax`` keyword argument.

        line-created
            When a new line was created this hook is executed and handed the
            the line as ``line`` keyword argument.

        before-line-update
            Before a line is updated with new coordinates this hook is executed
            and handed the line as ``line`` keyword argument.

        line-updated
            When a line was updated with new coordinates this hook is executed
            and handed the line as ``line`` keyword argument.

        Args:
            dataset (dict): the dataset to update the :attr:`figure` with
        """
        logger.debug(_("Updating the figure with dataset {}").format(dataset))
        now = datetime.datetime.utcnow()
        parser = dataset.get("parser", None)
        data = dataset.get("data", {})
        for quant, val in data.items():
            if val is None:
                continue
            quantiter = iter((quant,) if isinstance(quant, str) else quant)
            quantity, unit, key = (next(quantiter, None) for i in range(3))
            props = {
                "parser": parser,
                "quantity": quantity,
                "unit": unit,
                "key": key,
            }
            # make sure all values are numeric
            values = tuple(
                filter(
                    lambda x: isinstance(x, float),
                    map(to_float, to_tuple(val)),
                )
            )
            if not values:
                continue
            # determine matching axes
            ax = next(self.matching_axes(props), None)
            if ax is None:
                logger.debug(_("Didn't find matching axes. Adding new."))
                restrictions = {}
                if self.subplots_for is not None:
                    restrictions[self.subplots_for] = props[self.subplots_for]
                ax = self.add_axes(restrictions=restrictions)
            self.call_registered_functions(
                "matching-axes-found", ax=ax, props=props
            )
            # determine matching line
            line = next(self.matching_line(props), None)
            if line:
                self.call_registered_functions("before-line-update", line=line)
                self.update_line(line=line, dataset=dataset, values=values)
                self.call_registered_functions("line-updated", line=line)
            else:
                logger.debug(
                    _("No line on {} matches {}. Plotting new.").format(
                        ax, props
                    )
                )
                coords = iter(
                    self.new_line_coords(values=values, dataset=dataset)
                )
                x, y = next(coords), next(coords)
                extra_plot_kwargs = next(coords, {})
                attrs = next(coords, {})
                plot_kwargs = {
                    "label": " ".join(
                        ([quantity] if quantity else [])
                        + ([key] if key else [])
                        + (["[{}]".format(unit)] if unit else [])
                        + (["({})".format(parser)] if parser else [])
                    )
                }
                plot_kwargs.update(extra_plot_kwargs)
                lines = ax.plot(x, y, **plot_kwargs)
                for cur_line in lines:
                    cur_line.restrictions = {
                        k: v
                        for k, v in props.items()
                        if k not in ax.restrictions
                    }
                    for attr, v in attrs.items():
                        setattr(cur_line, attr, v)
                    self.call_registered_functions(
                        "line-created", line=cur_line
                    )
                ax.legend()

    @SubPlotsAnimator.register_method("before-each-frame")
    def optimal_subplots_layout(self, *args, **kwargs):
        current_ratio = functools.reduce(
            operator.truediv, self.figure.get_size_inches()
        )
        if (
            self.figure.last_ratio
            if hasattr(self.figure, "last_ratio")
            else None
        ) != current_ratio and len(self.figure.axes):
            self.reorder_subplots()
            self.figure.last_ratio = current_ratio

    @SubPlotsAnimator.register_method("key-pressed")
    def toggle_normed(self, event):
        """
        Callback to toggle :any:`only_expand_view` if the pressed
        key was an ``e``.

        .. hint::

            This means, you can press ``e`` when using a :any:`LinesAnimator`
            to toggle axis expanding.

        Args:
            event (matplotlib.backend_bases.KeyEvent, optional): the key event
        """
        if event.key == "e":
            if self.only_expand_view:
                logger.info(_("Stop always expanding the view"))
            else:
                logger.info(_("Will not only expand the view"))
            self.only_expand_view = not self.only_expand_view

    def update_figure(self, buffer):
        """
        If :any:`paused`, return. Otherwise, :any:`update_figure_with_dataset`
        for all datasets in the given buffer.

        The following registry hooks are executed:

        before-each-frame
            first thing that is done in this function (and before pausing)

        after-each-frame
            last thing that is done in this function

        Args:
            buffer (list-like): the buffer containing the datasets
                to update the :attr:`figure` with.
        """
        # call functions registered for before the frame
        self.call_registered_functions("before-each-frame", buffer)
        if self.paused:
            return
        # update the figure with all buffered datasets
        for dataset in buffer:
            self.update_figure_with_dataset(dataset)
        # call functions registered for after the frame
        self.call_registered_functions("after-each-frame")

    def fit_view(self, axes, only_expand=None):
        """
        Fit the view to the data. If ``only_expand_view`` is ``True``, both
        axis limits are only expanded and never shrinked except when resetting
        the previous respective extremes by changing the axis scale (e.g. by
        hitting the ``l`` or ``k`` key).

        Args:
            axes (sequence of str): iterable of values ``"x"`` and ``"y"``
            only_expand (bool, optional): Whether to only expand
        """
        only_expand = (
            self.only_expand_view if only_expand is None else only_expand
        )
        lim = {
            "x": {"min": "left", "max": "right"},
            "y": {"min": "bottom", "max": "top"},
        }
        for ax in self.figure.axes:
            ax.relim()
            if only_expand:
                for axis in axes:
                    set_lim = getattr(ax, "set_{}lim".format(axis))
                    set_lim_kwargs = {}
                    last_scale_attr = "last_{}scale".format(axis)
                    scale = getattr(ax, "get_{}scale".format(axis))()
                    last_scale = getattr(ax, last_scale_attr, None)
                    for func in (min, max):
                        side = func.__name__
                        attr = "{}lim_{}".format(axis, side)
                        data_lim = func(
                            func(getattr(line, "get_{}data".format(axis))())
                            for line in ax.get_lines()
                        )
                        if scale != last_scale:
                            if hasattr(ax, attr):
                                delattr(ax, attr)
                        ext_lim = getattr(ax, attr, data_lim)
                        new_lim = func(ext_lim, data_lim)
                        if np.isfinite(new_lim) and not (
                            "log" in scale
                            and (np.isclose(new_lim, 0) or new_lim <= 0)
                        ):
                            setattr(ax, attr, func(new_lim, data_lim))
                            set_lim_kwargs[lim[axis][side]] = new_lim
                    if (
                        not np.isclose(*(set_lim_kwargs.values()))
                        if len(set_lim_kwargs) == 2
                        else True
                    ):
                        set_lim(**set_lim_kwargs)
                    setattr(ax, last_scale_attr, scale)
            else:
                for attr in filter(
                    functools.partial(hasattr, ax),
                    (
                        "{}lim_{}".format(a, s)
                        for a, s in itertools.product(("xy"), ("min", "max"))
                    ),
                ):
                    delattr(ax, attr)
                ax.autoscale(
                    enable=True, axis="both" if axes == "xy" else axes
                )
                ax.autoscale_view()
