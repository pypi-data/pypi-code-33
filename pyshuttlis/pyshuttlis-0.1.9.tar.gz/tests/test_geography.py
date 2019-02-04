import pytest

from shuttlis.geography import Location


@pytest.mark.parametrize("lat,lng", [(90.0, 180.0), (-90.0, -180.0)])
def test_location_constructer_with_valid_values(lat, lng):
    loc = Location(lat, lng)
    assert lat == loc.lat
    assert lng == loc.lng


@pytest.mark.parametrize("lat,lng", [(90.0, 180.0), (-90.0, -180.0)])
def test_location_equality_hash(lat, lng):
    loc = Location(lat, lng)
    loc2 = Location(lat, lng)
    assert loc == loc2
    assert hash(loc) == hash(loc2)


@pytest.mark.parametrize("lat,lng", [(90, 190), (90.1, 179), (90.1, 180.001)])
def test_location_constructer_disallows_lat_lng_values_which_are_out_of_range(lat, lng):
    with pytest.raises(AssertionError):
        Location(lat, lng)
