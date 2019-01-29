# system modules
import sys
import threading
import inspect
import collections
import functools
import logging
import time
import datetime

# internal modules

# external modules


logger = logging.getLogger(__name__)


class Streamer(threading.Thread):
    """
    Class to asynchronously stream and buffer data from a
    :class:`polt.parser.parser.Parser` in a :class:`threading.Thread`.

    Args:
        parser (polt.parser.)
        buffer (list-like, optional): A buffer for the data. Defaults To a
            :class:`collections.deque`.
        flush_after (float, optional): Amount of seconds to buffer recieved
            before extending the :attr:`buffer` with it. Default is 0.
        max_rate (float, optional): Maximum data rate (datasets per second)
            to append to :attr:`buffer`. Default is unlimited.
    """

    def __init__(
        self, parser=None, buffer=None, flush_after=None, max_rate=None
    ):
        threading.Thread.__init__(
            self, daemon=True, name="{}Thread".format(type(self).__name__)
        )
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)[0]
        for arg in args[1:]:
            val = locals().get(arg)
            if val is not None:
                setattr(self, arg, val)

    @property
    def stopevent(self):
        """
        Event to stop the thread gracefully

        :type: :class:`threading.Event`
        """
        try:
            self._stopevent
        except AttributeError:  # pragma: no cover
            self._stopevent = threading.Event()
        return self._stopevent

    @property
    def parser(self):
        """
        The parser to buffer data from

        :type: :class:`polt.parser.parser.Parser`
        """
        try:
            self._parser
        except AttributeError:  # pragma: no cover
            self._parser = None
        return self._parser

    @parser.setter
    def parser(self, new_parser):
        try:
            iter(new_parser.data)
        except AttributeError:  # pragma: no cover
            raise ValueError(
                "{} object does not have a 'data' property".format(
                    type(new_parser).__name__
                )
            )
        except TypeError:  # pragma: no cover
            raise ValueError(
                "dataset property {} object is not iterable".format(
                    type(new_parser.data).__name__
                )
            )
        self._parser = new_parser

    @property
    def buffer(self):
        """
        Buffer for received data

        :type: list-like, i.e. something with :meth:`list.append` and
            :meth:`list.extend`-like methods
        :getter: Initializes an empty :class:`collections.deque`
            buffer if none is yet available
        """
        try:
            self._buffer
        except AttributeError:
            self._buffer = collections.deque()
        return self._buffer

    @buffer.setter
    def buffer(self, new_buffer):
        assert any(
            hasattr(new_buffer, attr) for attr in ("extend", "append")
        ), (
            "{} object does not neither have " "append() nor extend() method"
        ).format(
            type(new_buffer).__name__
        )
        self._buffer = new_buffer

    @property
    def flush_after(self):
        """
        Time frame to buffer recieved data before appending it to the
        :attr:`buffer`. Default is 0 seconds (immediately).

        :type: :class:`float` in seconds
        """
        try:
            self._flush_after
        except AttributeError:
            self._flush_after = 0
        return self._flush_after

    @flush_after.setter
    def flush_after(self, new):
        self._flush_after = abs(float(new))

    @property
    def max_rate(self):
        """
        Time frame to buffer recieved data before appending it to the
        :attr:`buffer`. Default is 0.1 seconds.

        :type: :class:`float` in datasets per second (Hz)
        """
        try:
            self._max_rate
        except AttributeError:
            self._max_rate = float("inf")
        return self._max_rate

    @max_rate.setter
    def max_rate(self, new):
        self._max_rate = abs(float(new)) if new is not None else None

    def run(self):
        """
        Continuously read data from :attr:`Streamer.parser` into
        :attr:`Streamer.buffer` by iterating over :attr:`Parser.data`. Also
        add a field ``time_recieved_utc`` to the dataset containing the value
        of :meth:`datetime.datetime.utcnow`.
        """
        logger.debug("Starting parser {}".format(repr(self.parser.name)))
        time_last_flush = float("-inf")
        time_recorded_last = float("-inf")
        buf = collections.deque()
        while True:
            if self.stopevent.is_set():
                logger.debug(_("stopevent is set, stop reading data"))
                break
            try:
                d = next(self.parser.data)
                logger.debug(
                    _("Received dataset {dataset} from {parser}").format(
                        dataset=repr(d), parser=repr(self.parser.name)
                    )
                )
                if (time.time() - time_recorded_last) > 1 / self.max_rate:
                    buf.append(
                        {
                            "time_recieved_utc": datetime.datetime.utcnow(),
                            "parser": self.parser.name,
                            "data": d,
                        }
                    )
                    time_recorded_last = time.time()
                if len(buf):
                    if (time.time() - time_last_flush) > self.flush_after:
                        self.buffer.extend(buf)
                        buf.clear()
                        time_last_flush = time.time()
            except StopIteration:
                logger.info(
                    _("No more {} data on {}").format(
                        type(self.parser).__name__, repr(self.parser.name)
                    )
                )
                break

    def stop(self):
        """
        Stop this thread gracefully, finishing just reading the current dataset
        """
        logger.debug(_("Will stop buffering soon"))
        self.stopevent.set()

    def __del__(self):
        """
        Deconstructor
        """
        pass
