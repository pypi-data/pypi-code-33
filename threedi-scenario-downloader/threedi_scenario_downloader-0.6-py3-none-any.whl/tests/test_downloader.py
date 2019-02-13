# -*- coding: utf-8 -*-
"""Tests for downloader.py"""
from threedi_scenario_downloader import downloader
import configparser
import pytest
from requests.exceptions import HTTPError


def test_set_headers():
    config = configparser.ConfigParser()
    config.read("threedi_scenario_downloader/tests/testdata/realconfig.ini")
    downloader.set_headers(
        config["credentials"]["username"], config["credentials"]["password"]
    )


def test_get_headers():
    headers = downloader.get_headers()
    config = configparser.ConfigParser()
    config.read("threedi_scenario_downloader/tests/testdata/realconfig.ini")

    assert headers["username"] == config["credentials"]["username"]
    assert headers["password"] == config["credentials"]["password"]


def test_find_scenario_by_model_slug():
    r = downloader.find_scenarios_by_model_slug(
        "005a58d09538e4e4cdbe48f2f3f22aeb89330ae4"
    )
    assert r[0]["uuid"] == "06c38953-31ec-4f6d-ae1f-ccdf31a348ae"


def test_find_scenario_by_name():
    r = downloader.find_scenarios_by_name("lizardapitest")
    assert r[0]["uuid"] == "06c38953-31ec-4f6d-ae1f-ccdf31a348ae"


def test_get_netcdf_link():
    url = downloader.get_netcdf_link("06c38953-31ec-4f6d-ae1f-ccdf31a348ae")
    assert url == "https://demo.lizard.net/api/v3/scenario-results/52331/results_3di.nc"


def test_get_raster():
    raster = downloader.get_raster(
        "06c38953-31ec-4f6d-ae1f-ccdf31a348ae", "depth-max-dtri"
    )
    assert raster["uuid"] == "4ef95627-e370-4eba-a5bc-bed661a3101a"


def test_get_raster_temporal():
    raster = downloader.get_raster("06c38953-31ec-4f6d-ae1f-ccdf31a348ae", "depth-dtri")
    assert raster["uuid"] == "907132e8-931a-4b78-8cb1-bad52500be7a"


def test_get_raster_from_non_existing_scenario():
    with pytest.raises(HTTPError):
        raster = downloader.get_raster(
            "06c37953-31ec-4f6d-ae1f-ccdf31a348ae", "depth-max-dtri"
        )
        assert raster is not None


def test_create_raster_task():
    task = downloader.create_raster_task(
        downloader.get_raster("06c38953-31ec-4f6d-ae1f-ccdf31a348ae", "depth-max-dtri"),
        "EPSG:28992",
        "1000",
    )
    assert task is not None
