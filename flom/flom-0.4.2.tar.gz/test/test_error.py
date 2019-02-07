import flom

import pytest


def test_invalid_time(motion):
    with pytest.raises(flom.InvalidTimeError):
        motion.frame_at(-1)

    with pytest.raises(flom.InvalidTimeError):
        motion.frame_at(float('nan'))


def test_out_of_frames(oneshot_motion):
    with pytest.raises(flom.OutOfFramesError):
        oneshot_motion.frame_at(oneshot_motion.length() + 1)
