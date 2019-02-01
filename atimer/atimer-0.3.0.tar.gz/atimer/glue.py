#
# atimer - timer library for asyncio
#
# Copyright (C) 2016-2019 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Timer based on Linux `timerfd` interface.
"""

import asyncio
import logging
import os
import struct

from ._atimer import atimer_init, atimer_start, atimer_close

logger = logging.getLogger(__name__)

class Timer(object):
    """
    Timer based on Linux `timerfd` interface.
    """
    def __init__(self, interval):
        """
        Create timer object.

        :param interval: Interval, in seconds, at which the timer expires.
        """
        self._fd = atimer_init()
        self._interval = interval
        self._task = None
        self._loop = None

    def start(self):
        """
        Arm the timer.
        """
        self._loop = asyncio.get_event_loop()
        self._loop.add_reader(self._fd, self._timer_expired)
        atimer_start(self._fd, self._interval)
        if __debug__:
            logger.debug('timer armed')

    def __await__(self):
        """
        Wait for timer expiration.

        Return number of timer expirations. The number of expirations is
        usually `1` until timer overrun happens. Refer to POSIX
        documentation for definition of timer overrun.
        """
        self._task = self._loop.create_future()
        return (yield from self._task)

    def close(self):
        """
        Stop and disarm the timer.
        """
        self._loop.remove_reader(self._fd)
        atimer_close(self._fd)

        task = self._task
        if task and not task.done():
            task.set_exception(asyncio.CancelledError())

        if __debug__:
            logger.debug('timer disarmed')

    def _timer_expired(self):
        """
        Handle notification of timer expiration from the timer.

        Number of expirations is read from timer file descriptor and set as
        result of current task. If timer object is not awaited yet, then
        return null.
        """
        task = self._task
        if task and not task.done():
            value = os.read(self._fd, 8)
            value = struct.unpack('Q', value)[0]
            self._task.set_result(value)

# vim: sw=4:et:ai
