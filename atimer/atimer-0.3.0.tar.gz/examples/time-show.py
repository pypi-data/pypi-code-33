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

import asyncio
import time

import atimer

async def start(timer):
    timer.start()

    for i in range(6):
        if i == 3:  # simulation of overrun
            time.sleep(1.1)

        num_exp = await timer

        now = time.time()
        print('{}: {:.3f}  {}'.format(i, now, num_exp))

timer = atimer.Timer(0.25)
try:
    asyncio.run(start(timer))
finally:
    timer.close()

# vim: sw=4:et:ai
