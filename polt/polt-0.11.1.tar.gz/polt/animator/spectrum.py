# system modules
import functools
import itertools
import sys
import datetime
import logging
import inspect
import operator
import re

# internal modules
from polt.animator.lines import LinesAnimator
from polt.utils import *

# external modules
import numpy as np
import scipy.interpolate
import scipy.signal
import scipy.fftpack
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class SpectrumAnimator(LinesAnimator):
    """
    Animator to display recieved data as lines.

    Args:
        args, kwargs: further arguments handed to the
            :any:`LinesAnimator` constructor.
        blocks (int, optional): Into how many block-wise averages should be
            taken of the FFT. Default is to not split the data up.
        hanning (bool, optional): Whether to apply a
            :any:`numpy.hanning`-window before the FFT. Default is ``True``.
        time_frame (int, optional): displayed time frame in seconds. By default
            (``None``), all times are diplayed.
    """

    def __init__(self, *args, time_frame=None, hanning=None, **kwargs):
        LinesAnimator.__init__(self, *args, **kwargs)
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)[0]
        for arg in args[1:]:
            val = locals().get(arg)
            if val is not None:
                setattr(self, arg, val)

    @property
    def hanning(self):
        """
        Whether to apply a :any:`numpy.hanning`-window before the FFT.

        .. note::

            Set this option from the command-line via
            ``polt live -a spectrum -o hanning=yes|no``

        :type: :class:`bool`
        """
        try:
            self._hanning
        except AttributeError:
            self._hanning = False
        return self._hanning

    @hanning.setter
    def hanning(self, new):
        self._hanning = new == "yes" if isinstance(new, str) else bool(new)

    @property
    def normed(self):
        """
        Whether to norm the spectrum with the frequency. Default is ``False``.

        .. note::

            Set this option from the command-line via
            ``polt live -a spectrum -o normed=yes|no``

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
    def detrend(self):
        """
        Whether to detrend the data before preforming the FFT.

        .. note::

            Set this option from the command-line via
            ``polt live -a spectrum -o detrend=yes|no``

        :type: :class:`str` or ``None``
        """
        try:
            self._detrend
        except AttributeError:
            self._detrend = True
        return self._detrend

    @detrend.setter
    def detrend(self, new):
        self._detrend = new == "yes" if isinstance(new, str) else bool(new)

    @property
    def blocks(self):
        """
        Into how many blocks to split the data for later averaging of the FFT.
        Default is to not split the data up.

        .. note::

            Set this option from the command-line via
            ``polt live -a spectrum -o blocks=N``

        :type: :class:`bool`
        """
        try:
            self._blocks
        except AttributeError:
            self._blocks = 1
        return self._blocks

    @blocks.setter
    def blocks(self, new):
        self._blocks = max(1, int(new))

    @property
    def time_frame(self):
        """
        Time frame to use in seconds. Data outside that window
        will be dropped.

        .. note::

            Set this option from the command-line via
            ``polt live -a spectrum -o time-frame=SECONDS``

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
            ``polt live -a spectrum -o show-data-rate=yes|no``

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

    def spectrum(
        self, x, y, hanning=None, blocks=None, normed=None, detrend=None
    ):
        """
        Call :any:`numpy.fft.fft` and :any:`numpy.fft.fftfreq` with default
        arguments.

        Args:
            x,y (sequences of floats): x and y values
            hanning (bool, optional): whether to apply a Hanning window
            normed (bool, optional): whether to norm the power spectrum with
                the frequency.
            detrend (bool, optional): whether to detrend the data first

        Returns:
            sequence : frequencies, power as arrays
        """
        hanning = self.hanning if hanning is None else hanning
        blocks = self.blocks if blocks is None else blocks
        normed = self.normed if normed is None else normed
        detrend = self.detrend if detrend is None else detrend
        # convert inputs to numpy arrays
        x, y = map(np.asarray, (x, y))
        # drop older values to fit the number of blocks
        if x.size > blocks:
            drop = x.size % blocks
            x, y = x[drop:], y[drop:]
        # interpolate to evenly-spaced times
        if x.size > 1:
            interpolator = scipy.interpolate.interp1d(x, y)
            x = np.linspace(x.min(), x.max(), num=x.size)
            y = interpolator(x)
        # detrend
        if detrend:
            y = scipy.signal.detrend(y)
        # calculate power spectrum
        power = (
            np.abs(
                # calculate average across block means
                np.mean(
                    # stack fft block resuls
                    np.vstack(
                        tuple(
                            # Fourrier transformation
                            map(
                                scipy.fftpack.fft,
                                # apply hanning window if desired
                                map(
                                    lambda a: a * np.hanning(a.size)
                                    if hanning
                                    else a,
                                    # split y into blocks
                                    np.split(y, blocks)
                                    if y.size > blocks
                                    else (y,),
                                ),
                            )
                        )
                    ),
                    axis=0,
                )
            )
            ** 2
        )
        # calculate frequencies
        freq = np.fft.fftfreq(power.size, ((x.max() - x.min()) / x.size) or 1)
        # sort frequencies
        idx = np.argsort(freq)
        freq, power = freq[idx], power[idx]
        positive_freq = freq >= 0
        return (
            freq[positive_freq],
            power[positive_freq] / (freq[positive_freq] if normed else 1),
        )

    def new_line_coords(self, values, dataset={}):
        new_value = np.mean(np.array(values))
        new_time = np.datetime64(
            dataset.get("time_recieved_utc", datetime.datetime.utcnow())
        )
        times, values = new_time.reshape(-1), new_value.reshape(-1)
        freq, fft = self.spectrum(
            (times - times.min()) / np.timedelta64(1, "s"), values
        )
        return freq, fft, {}, {"times": times, "values": values}

    def update_line(self, line, values, dataset={}):
        line.values = np.append(line.values, values)
        line.times = np.append(
            line.times,
            np.datetime64(
                dataset.get("time_recieved_utc", datetime.datetime.utcnow())
            ),
        )
        freq, fft = self.spectrum(
            (line.times - line.times.min()) / np.timedelta64(1, "s"),
            line.values,
        )
        line.set_xdata(freq)
        line.set_ydata(fft)

    @LinesAnimator.register_method("key-pressed")
    def toggle_normed(self, event):
        """
        Callback to toggle :any:`normed` if the pressed
        key was an ``n``.

        .. hint::

            This means, you can press ``n`` when using the
            :any:`SpectrumAnimator` to switch between normed and unnormed
            spectra.

        Args:
            event (matplotlib.backend_bases.KeyEvent, optional): the key event
        """
        if event.key == "n":
            self.normed = not self.normed
            for ax in self.figure.axes:
                self.update_ylabel(ax)

    @LinesAnimator.register_method("key-pressed")
    def toggle_detrend(self, event):
        """
        Callback to toggle :any:`detrend` if the pressed
        key was an ``d``.

        .. hint::

            This means, you can press ``d`` when using the
            :any:`SpectrumAnimator` to toggle detrending.

        Args:
            event (matplotlib.backend_bases.KeyEvent, optional): the key event
        """
        if event.key == "d":
            self.detrend = not self.detrend
            for ax in self.figure.axes:
                self.update_ylabel(ax)

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

    @LinesAnimator.register_method("after-each-frame")
    def adjust_view(self, *args, **kwargs):
        """
        Adjust the view with :any:`LinesAnimator.fit_view` for both axes.
        """
        self.fit_view(axes="xy")

    def update_ylabel(self, ax):
        ax.set_ylabel(
            " ".join(
                [
                    _("power"),
                    "({})".format(_("normed")) if self.normed else "",
                    "({})".format(_("detrended")) if self.detrend else "",
                    " ".join(
                        r"[${}^2${}]".format(
                            unit, "/{}".format(_("Hz")) if self.normed else ""
                        )
                        for unit in sorted(
                            u if u is not None else _("unitless")
                            for u in ax.units
                        )
                    ),
                ]
            )
        )

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
            self.update_ylabel(ax)

    @LinesAnimator.register_method("axes-added")
    def set_axes_labels(self, ax):
        ax.set_ylabel(_("power"))
        ax.set_xlabel(_("frequency [{}]").format(_("Hz")))

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
                    x = line.times
                    tdiff = (
                        line.times.max() - line.times.min()
                    ) / np.timedelta64(1, "s")
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
