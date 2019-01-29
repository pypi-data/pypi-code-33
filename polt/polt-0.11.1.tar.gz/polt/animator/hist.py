# system modules
import functools
import datetime
import logging
import inspect
import operator
import sys

# internal modules
from polt.animator.lines import LinesAnimator
from polt.utils import *

# external modules
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class HistAnimator(LinesAnimator):
    """
    Animator to display recieved data as lines.

    Args:
        args, kwargs: further arguments handed to the
            :any:`LinesAnimator` constructor.
        bins (int, optional): the number of bins to use.
        normed (bool, optional): whether to display density instead of
            frequency. Default is ``False``.
        time_frame (int, optional): displayed time frame in seconds. By default
            (``None``), all times are diplayed.
    """

    def __init__(
        self, *args, bins=None, normed=None, time_frame=None, **kwargs
    ):
        LinesAnimator.__init__(self, *args, **kwargs)
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)[0]
        for arg in args[1:]:
            val = locals().get(arg)
            if val is not None:
                setattr(self, arg, val)

    @property
    def bins(self):
        """
        How many bins to use. Default is 10.

        .. note::

            Set this option from the command-line via
            ``polt live -a hist -o bins=NUMBER``

        :type: :class:`str` or ``None``
        """
        try:
            self._bins
        except AttributeError:
            self._bins = 10
        return self._bins

    @bins.setter
    def bins(self, new):
        self._bins = max(2, abs(int(new)))

    @property
    def normed(self):
        """
        Whether to norm the histogram. By default (``False``), the
        absolute frequency is used.

        .. note::

            Set this option from the command-line via
            ``polt live -a hist -o normed=yes|no``

        :type: :class:`str` or ``None``
        """
        try:
            self._normed
        except AttributeError:
            self._normed = False
        return self._normed

    @normed.setter
    def normed(self, new):
        self._normed = new == "yes" if isinstance(new, str) else bool(new)

    @property
    def time_frame(self):
        """
        Time frame to use in seconds. Data outside that window
        will be dropped.

        .. note::

            Set this option from the command-line via
            ``polt live -a hist -o time-frame=SECONDS``

        :type: :class:`int` or ``None``
        """
        try:
            self._time_frame
        except AttributeError:
            self._time_frame = None
        return self._time_frame

    @time_frame.setter
    def time_frame(self, new):
        self._time_frame = max(sys.float_info.min, int(new))

    @property
    def show_data_rate(self):
        """
        Whether to show the displayed data rate in the legend label. The
        default is ``False``.

        .. note::

            Set this option from the command-line via
            ``polt live -a hist -o show-data-rate=yes|no``

        :type: :class:`bool`
        """
        try:
            self._show_data_rate
        except AttributeError:
            self._show_data_rate = False
        return self._show_data_rate

    @show_data_rate.setter
    def show_data_rate(self, new):
        self._show_data_rate = (
            new == "yes" if isinstance(new, str) else bool(new)
        )

    def histogram(self, *args, **kwargs):
        """
        Call :any:`numpy.histogram` with default arguments.

        Args:
            **kwargs: overwriting keyword arguments

        Returns:
            sequence : the same as :any:`numpy.histogram`
        """
        hist_kwargs = {"bins": self.bins, "density": self.normed}
        hist_kwargs.update(kwargs)
        return np.histogram(*args, **hist_kwargs)

    def new_line_coords(self, values, dataset={}):
        time_recieved_utc = np.datetime64(
            dataset.get("time_recieved_utc", datetime.datetime.utcnow())
        )
        values = np.array(values)
        times = np.repeat(np.datetime64(time_recieved_utc), values.size)
        freq, bins = self.histogram(values)
        x = np.repeat(bins, 2)
        y = np.concatenate([np.array([0]), np.repeat(freq, 2), np.array([0])])
        return x, y, {}, {"times": times, "values": values}

    def update_line(self, line, values, dataset={}):
        time_recieved_utc = np.datetime64(
            dataset.get("time_recieved_utc", datetime.datetime.utcnow())
        )
        values = np.array(values)
        times = np.repeat(np.datetime64(time_recieved_utc), values.size)
        line.values = np.append(line.values, values)
        line.times = np.append(line.times, times)
        freq, bins = self.histogram(line.values)
        line.set_xdata(np.repeat(bins, 2))
        line.set_ydata(
            np.concatenate([np.array([0]), np.repeat(freq, 2), np.array([0])])
        )

    @LinesAnimator.register_method("key-pressed")
    def toggle_normed(self, event):
        """
        Callback to toggle :any:`normed` if the pressed
        key was an ``n``.

        .. hint::

            This means, you can press ``n`` when using the :any:`HistAnimator`
            to switch between normed and absolute histograms.

        Args:
            event (matplotlib.backend_bases.KeyEvent, optional): the key event
        """
        if event.key == "n":
            self.normed = not self.normed
            for ax in self.figure.axes:
                self.set_axes_labels(ax)

    @LinesAnimator.register_method("before-line-update")
    def drop_old_values(self, line):
        if self.time_frame:
            outside = (
                np.datetime64(datetime.datetime.utcnow()) - line.times
            ) / np.timedelta64(1, "s") > self.time_frame
            if outside.any():
                outside_ind = np.where(outside)[0]
                line.values = np.delete(line.values, outside_ind)
                line.times = np.delete(line.times, outside_ind)

    @LinesAnimator.register_method("matching-axes-found")
    def set_units(self, ax, props={}):
        """
        Update the figure with a single dataset

        Args:
            ax (matplotlib.axes.Axes): the axes
            props (dict, optional): properties of the current dataset
        """
        unit = props.get("unit")
        if not hasattr(ax, "units"):
            ax.units = set()
        if unit not in ax.units:
            ax.units.add(unit)

    @LinesAnimator.register_method("axes-added")
    def set_axes_labels(self, ax):
        ax.set_ylabel(_("density") if self.normed else _("frequency"))
        ax.set_xlabel(_("value"))

    @LinesAnimator.register_method("after-each-frame")
    def adjust_view(self, *args, **kwargs):
        """
        Adjust the view with :any:`LinesAnimator.fit_view` for both axes.
        """
        self.fit_view(axes="xy")

    @LinesAnimator.register_method("after-each-frame")
    def update_data_rate_in_legends(self, *args, **kwargs):
        """
        If :any:`show_data_rate` is ``True``, update the displayed data rate in
        each line's legend.
        """
        now = datetime.datetime.utcnow()
        for ax in self.figure.axes:
            for line in ax.get_lines():
                if self.show_data_rate:
                    x = line.get_xdata()
                    if (
                        line.last_extrapolated
                        if hasattr(line, "last_extrapolated")
                        else False
                    ):
                        x = x[:-1]
                    tdiff = (max(x.max(), now) - x.min()).total_seconds()
                    rate = max(x.size - 1, 0) / tdiff if tdiff > 0 else 0
                    rate_val, rate_str = (
                        (1 / rate, _("sec/ds"))
                        if (0 < rate < 1)
                        else (rate, _("Hz"))
                    )
                    rate_text = "({:.1f} {})".format(rate_val, rate_str)
                    rate_text_pattern = r"\([^)]+?({}|{})\)".format(
                        re.escape(_("Hz")), re.escape(_("sec/ds"))
                    )
                    old_label = new_label = line.get_label()
                    if re.search(rate_text_pattern, old_label):
                        new_label = re.sub(
                            rate_text_pattern, rate_text, old_label
                        )
                    else:
                        new_label += " " + rate_text
                    if old_label != new_label:
                        line.set_label(new_label)
                        ax.legend()
