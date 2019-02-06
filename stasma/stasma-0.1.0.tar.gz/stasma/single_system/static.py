from astropy import units as u
from stasma import units, const


def angular_velocity(rotation_period):
    """
    rotational angular velocity of the star
    :return:
    """
    return const.FULL_ARC / (rotation_period * units.PERIOD_UNIT).to(u.s).value
