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

import time

from atimer._atimer import to_timespec, timespec_add
from atimer import Timer

import pytest

NANOSEC = 10 ** 9

def test_to_timespec():
    """
    Test converting float number to `timespec` values, this is second and
    number of nanoseconds.
    """
    sec, nsec = to_timespec(1.01)
    assert 1 == sec
    assert 10 ** 7 == nsec

def test_timespec_add():
    """
    Test adding time to `timespec` structure.
    """
    t = {'tv_sec': 10, 'tv_nsec': 0.1 * NANOSEC}
    result = timespec_add(t, 1, 0.95 * NANOSEC)
    assert 12 == result['tv_sec']
    assert 0.05 * NANOSEC == result['tv_nsec']

@pytest.mark.asyncio
@pytest.mark.parametrize('interval', [0.1, 0.25, 0.6, 1, 2])
async def test_sync_edge_full(interval):
    """
    Test synchronizing timer to the edge of interval of realtime clock.
    """
    timer = Timer(interval)
    timer.start()
    await timer
    result = -time.time() % interval
    assert interval == pytest.approx(result, abs=0.001)

# vim: sw=4:et:ai
