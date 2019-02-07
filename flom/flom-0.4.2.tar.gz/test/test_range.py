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


def test_key_range_joint(motion):
    j1 = set(motion.joint_names())
    j2 = set(motion.frame_at(0).positions.keys())
    assert j1 == j2


def test_key_range_effector(motion):
    e1 = set(motion.effector_names())
    e2 = set(motion.frame_at(0).effectors.keys())
    assert e1 == e2


def test_frame_range(oneshot_motion):
    for t, frame in oneshot_motion.frames(1):
        assert frame == oneshot_motion.frame_at(t)


def test_keyframe_range(oneshot_motion):
    for t, frame in oneshot_motion.keyframes():
        assert frame == oneshot_motion.frame_at(t)


def test_keyframe_range_assign(oneshot_motion):
    empty_frame = oneshot_motion.new_keyframe()
    for t, frame in oneshot_motion.keyframes():
        oneshot_motion.insert_keyframe(t, empty_frame)
    for _, frame in oneshot_motion.keyframes():
        assert frame == empty_frame
