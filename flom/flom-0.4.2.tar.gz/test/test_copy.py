#
# Copyright 2018 coord.e
#
# This file is part of flom-py.
#
# flom-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# flom-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with flom-py.  If not, see <http://www.gnu.org/licenses/>.
#

import flom


def test_copy_motion_equal(motion):
    m2 = flom.Motion(motion)
    assert m2 == motion


def test_copy_motion_noref(motion):
    m2 = flom.Motion(motion)
    m2.set_model_id("***")
    assert m2 != motion


def test_copy_frame_equal(frame):
    frame2 = flom.Frame(frame)
    assert frame2 == frame


def test_copy_frame_noref(frame):
    frame2 = flom.Frame(frame)
    frame2.set_position("***", 0)
    assert frame2 != frame


def test_copy_effector_equal(effector):
    effector2 = flom.Effector(effector)
    assert effector2 == effector


def test_copy_effector_noref(effector):
    effector2 = flom.Effector(effector)
    if effector.location is None:
        effector2.location = flom.Location()
    else:
        effector2.location = None
    assert effector2 != effector
