import pytest

from .fixtures import test_location_geojson
from rcm.model import HouseholdsFirstActivation
from mesa_geo import GeoAgent


def test_no_scheduler(test_location_geojson):
    with pytest.raises(Exception):
        ResidentialChoiceModel(test_location_geojson, 1, None, None)


def test_no_initialize(test_location_geojson):
    with pytest.raises(Exception):
        ResidentialChoiceModel(test_location_geojson, 1, HouseholdsFirstActivation(), None)
