# system modules
import functools
import collections
import time
import itertools
import logging
import inspect
import math
from abc import abstractmethod

# internal modules
from polt.filter import Filter
from polt.registry import FunctionRegistry

# external modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

logger = logging.getLogger(__name__)


class Animator(FunctionRegistry):
    """
    The :class:`Animator` is an abstract base class for animations. Subclasses
    need to override just the :meth:`Animator.update_figure` method.

    Args:
        figure (matplotlib.figure.Figure, optional): the figure to animate on
        buffer (list-like, optional): the buffer to retrieve
            data from
        filters (sequence of Filter objects, optional): filters to modify
            datasts with
    """

    def __init__(self, figure=None, buffer=None, filters=None):
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)[0]
        for arg in args[1:]:
            val = locals().get(arg)
            if val is not None:
                setattr(self, arg, val)

    def modifies_animation(decorated_function):
        """
        Decorator for methods that require resetting the animation
        """

        @functools.wraps(decorated_function)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "_animation"):
                logger.debug(
                    _("Clearing animation before {}").format(
                        decorated_function
                    )
                )
                del self._animation
            return decorated_function(self, *args, **kwargs)

        return wrapper

    @property
    def buffer(self):
        """
        The buffer to retrieve data from

        :type: list-like
        """
        try:
            self._buffer
        except AttributeError:  # pragma: no cover
            self._buffer = list()
        return self._buffer

    @buffer.setter
    def buffer(self, new):
        self._buffer = new

    @property
    def filters(self):
        """
        The filters to modify datasets with

        :type: list-like
        """
        try:
            self._filters
        except AttributeError:  # pragma: no cover
            self._filters = list()
        return self._filters

    @filters.setter
    def filters(self, new):
        self._filters = new

    @property
    def interval(self):
        """
        The frame update interval

        .. note::

            Set this option from the command-line via
            ``polt live -a lines -o interval=MILLISECONDS``

        :type: :any:`int`
        """
        try:
            self._interval
        except AttributeError:
            self._interval = 200
        return self._interval

    @interval.setter
    def interval(self, new_interval):
        self._interval = max(1, int(new_interval))

    @property
    def max_fps(self):
        """
        The maximum update framerate in frames per second (Hz). Internally this
        sets :any:`interval`.

        .. note::

            Set this option from the command-line via
            ``polt live -a lines -o max-fps=FRAMERATE``

        :getter: return the inverse of :attr:`interval`
        :setter: set :attr:`interval` to the inverse of the given value in
            millisecons capped below ``1e-2`` which means 100 seconds per frame
            (very slow...)
        :type: :class:`float`
        """
        return 1 / self.interval

    @max_fps.setter
    def max_fps(self, new):
        self.interval = 1e3 / max(1e-2, float(new))

    @property
    def show_fps(self):
        """
        Whether to show the current plot framerate in the title.
        Default is ``False``.

        .. note::

            Set this option from the command-line via
            ``polt live -o show-fps=yes|no``

        :type: :class:`bool`
        """
        try:
            self._show_fps
        except AttributeError:
            self._show_fps = False
        return self._show_fps

    @show_fps.setter
    def show_fps(self, new):
        self._show_fps = new == "yes" if isinstance(new, str) else bool(new)

    @property
    def figure(self):
        """
        The figure to animate on

        :type: :class:`matplotlib.figure.Figure`
        """
        try:
            self._figure
        except AttributeError:  # pragma: no cover
            fig = plt.figure()
            fig.canvas.mpl_connect(
                "key_press_event",
                lambda e: self.call_registered_functions(
                    "key-pressed", event=e
                ),
            )
            self._figure = fig
        return self._figure

    @figure.setter
    @modifies_animation
    def figure(self, new):
        self._figure = new

    @property
    def animation(self):
        """
        The underlying animation

        :type: :class:`matplotlib.animation.FuncAnimation`
        """
        try:
            self._animation
        except AttributeError:
            self._animation = FuncAnimation(
                fig=self.figure,
                init_func=self.clear_figure,
                func=self.update_figure,
                frames=self.dataset,
                interval=self.interval,
                repeat=False,
            )
        return self._animation

    @property
    def paused(self):
        """
        Whether the animation is currently paused or not.
        During pause, recieved data is dropped if
        :attr:`Animator.drop_on_pause` is ``True``.

        :type: :class:`bool`
        """
        try:
            self._paused
        except AttributeError:
            self._paused = False
        return self._paused

    @paused.setter
    def paused(self, new):
        new = bool(new)
        if self.paused != new:
            if new:
                self.figure.canvas.set_window_title(
                    "{} ({})".format(_("polt").title(), _("paused"))
                )
            else:
                self.figure.canvas.set_window_title(_("polt").title())
        self._paused = new

    @property
    def drop_on_pause(self):
        """
        Whether to drop recieved data if the animation is paused. The default
        is ``False``.

        .. note::

            Set this option from the command-line via
            ``polt live -o drop-on-pause=yes|no``

        :type: :class:`bool`
        """
        try:
            self._drop_on_pause
        except AttributeError:
            self._drop_on_pause = False
        return self._drop_on_pause

    @drop_on_pause.setter
    def drop_on_pause(self, new):
        self._drop_on_pause = (
            new == "yes" if isinstance(new, str) else bool(new)
        )

    @property
    def fps_buffer(self):
        """
        Buffer to calculate the fps
        """
        try:
            self._fps_buffer
        except AttributeError:
            self._fps_buffer = collections.deque(maxlen=30)
        return self._fps_buffer

    def pause(self):
        """
        Pause the animation
        """
        self.paused = True

    def resume(self):
        """
        Resume the animation
        """
        self.paused = False

    def toggle_pause(self):
        """
        Change the paused state
        """
        if self.paused:
            logger.info(_("Resuming"))
        else:
            logger.info(_("Pausing"))
            if self.drop_on_pause:
                logger.info(_("Recieved data is dropped form now on."))
            else:
                logger.info(_("Data recording keeps going."))
        self.paused = not self.paused

    @FunctionRegistry.register_method("key-pressed")
    def toggle_pause_key_callback(self, event):
        """
        Callback to pause the animation with :any:`toggle_pause` if the pressed
        key was the spacebar.

        Args:
            event (matplotlib.backend_bases.KeyEvent, optional): the key event
        """
        if event.key == " ":
            self.toggle_pause()

    @FunctionRegistry.register_method("key-pressed")
    def toggle_show_fps(self, event):
        """
        Callback to toggle :any:`show_fps` if the pressed key was a capital
        ``F``.

        Args:
            event (matplotlib.backend_bases.KeyEvent, optional): the key event
        """
        if event.key == "F":
            self.show_fps = not self.show_fps
            self.figure.canvas.set_window_title(_("polt").title())

    def clear_figure(self):
        """
        Clear the :attr:`figure` by calling
        :meth:`matplotlib.figure.Figure.clear`.
        """
        self.figure.clear()
        self.figure.canvas.set_window_title(_("polt").title())

    @abstractmethod
    def update_figure(self, buffer):
        """
        Update the :attr:`figure` with a sequence of datasets from the
        :attr:`Animator.buffer`.

        .. note::

            This is an :func:`abc.abstractmethod`, so subclasses have to
            override this.

        Args:
            buffer (sequence): the buffer containing the datasets
                to update the :attr:`figure` with.
        """

    @property
    def dataset(self):
        """
        Endless-loop generator which :class:`list`-ifies the
        :attr:`Animator.buffer`, clears it and yields **another generator**
        yielding non-empty datasets filtered with :any:`filters`.  If
        :any:`paused` and :any:`drop_on_pause` is ``True``, drop the data.

        The following registry hooks are executed:

        frame-before-data-check
            first thing in each iteration

        frame-during-pause
            on each iteration but only during pause before dropping the
            :any:`buffer`

        frame-when-not-paused
            on each iteration but only during pause before reading and clearing
            the :any:`buffer`
        """
        filter_chain = Filter.chain(*self.filters)
        while True:
            self.call_registered_functions("frame-before-data-check")
            if self.paused:
                self.call_registered_functions("frame-during-pause")
                if self.drop_on_pause:
                    # empty the buffer
                    del self.buffer[:]
            else:
                self.call_registered_functions("frame-when-not-paused")
                # read the whole buffer
                buf = list(self.buffer)
                # empty the buffer
                del self.buffer[:]
            # remember the time we yielded this dataset
            self.fps_buffer.append(time.time())
            # modify datasets with the filters and ignore empty datasets
            yield filter(bool, map(filter_chain, buf))

    def run(self):
        """
        Run the animation by calling :func:`matplotlib.pyplot.show`
        """
        self.animation
        logger.debug(_("Showing the plot"))
        plt.show()
        logger.debug(_("Plot was closed"))

    @FunctionRegistry.register_method("frame-before-data-check")
    def update_window_title(self):
        if self.show_fps:
            n = len(self.fps_buffer)
            if n > 1:
                fps = n / (max(self.fps_buffer) - min(self.fps_buffer))
                self.figure.canvas.set_window_title(
                    " ".join(
                        (
                            _("polt").title(),
                            "({:.0f} {})".format(fps, _("fps")),
                        )
                    )
                )
