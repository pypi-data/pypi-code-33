# -*- coding: utf-8 -*-
"""Tests for downloader.py"""
from threedi_scenario_downloader import downloader
import configparser


def test_set_headers():
    config = configparser.ConfigParser()
    config.read("threedi_scenario_downloader/tests/testdata/realconfig.ini")
    downloader.set_headers(
        config["credentials"]["username"], config["credentials"]["password"]
    )


def test_download_maximum_waterdepth_raster():
    if True:
        downloader.download_maximum_waterdepth_raster(
            "06c38953-31ec-4f6d-ae1f-ccdf31a348ae",
            "EPSG:28992",
            resolution=1000,
            bounds=None,
            pathname="threedi_scenario_downloader/tests/testdata/max_waterdepth.tif",
        )


def test_download_waterdepth_raster():
    if True:
        downloader.download_waterdepth_raster(
            "06c38953-31ec-4f6d-ae1f-ccdf31a348ae",
            "EPSG:28992",
            1000,
            "2018-06-02T06:00:00Z",
            None,
            "threedi_scenario_downloader/tests/testdata/waterdepth.tif",
        )


def test_get_netcdf_link():
    url = downloader.get_netcdf_link("06c38953-31ec-4f6d-ae1f-ccdf31a348ae")
    assert url == "https://demo.lizard.net/api/v3/scenario-results/52331/results_3di.nc"


def test_download_raw_results():
    downloader.download_raw_results(
        "06c38953-31ec-4f6d-ae1f-ccdf31a348ae",
        "threedi_scenario_downloader/tests/testdata/test.nc",
    )
    assert True


def test_download_grid_administration():
    downloader.download_grid_administration(
        "06c38953-31ec-4f6d-ae1f-ccdf31a348ae",
        "threedi_scenario_downloader/tests/testdata/test.h5",
    )
    assert True


def test_clear_inbox():
    result = downloader.clear_inbox()
    assert result


def test_get_attachment_links():
    scenario = downloader.find_scenarios_by_name("lizardapitest")[0]
    links = downloader.get_attachment_links(scenario)
    assert links is not None


def test_rasters_in_scenario():
    scenario = downloader.find_scenarios_by_name("lizardapitest")[0]
    static_rasters, temporal_rasters = downloader.rasters_in_scenario(scenario)
    assert static_rasters is not None and temporal_rasters is not None


def test_get_raster_link():
    raster = downloader.get_raster(
        "06c38953-31ec-4f6d-ae1f-ccdf31a348ae", "depth-max-dtri"
    )
    download_url = downloader.get_raster_link(
        raster, "EPSG:4326", 10, bounds=None, time=None
    )
    assert download_url is not None


def test_get_static_rasters_links():
    scenario = downloader.find_scenarios_by_name("lizardapitest")[0]
    static_rasters, _ = downloader.rasters_in_scenario(scenario)
    static_rasters = [x for x in static_rasters if x["spatial_bounds"]]
    static_rasters_urls = downloader.get_static_rasters_links(
        static_rasters, "EPSG:4326", 10, bounds=None, time=None
    )
    assert isinstance(static_rasters_urls, dict)


def test_get_temporal_raster_links():
    scenario = downloader.find_scenarios_by_name("lizardapitest")[0]
    _, temporal_rasters = downloader.rasters_in_scenario(scenario)
    temporal_rasters = [x for x in temporal_rasters if x["spatial_bounds"]]
    temporal_raster = temporal_rasters[0]

    temporal_raster_urls = downloader.get_temporal_raster_links(
        temporal_raster, "EPSG:4326", 10, bounds=None, interval_hours=None
    )
    assert isinstance(temporal_raster_urls, dict) and len(temporal_raster_urls) > 1


def test_get_temporal_rasters_links():
    scenario = downloader.find_scenarios_by_name("lizardapitest")[0]
    _, temporal_rasters = downloader.rasters_in_scenario(scenario)
    temporal_rasters = [x for x in temporal_rasters if x["spatial_bounds"]]
    temporal_rasters_urls = downloader.get_temporal_rasters_links(
        temporal_rasters, "EPSG:4326", 10, bounds=None, interval_hours=None
    )
    assert isinstance(temporal_rasters_urls, dict)


def test_get_raster_timesteps():
    raster = downloader.get_raster("06c38953-31ec-4f6d-ae1f-ccdf31a348ae", "s1-dtri")
    timesteps = downloader.get_raster_timesteps(raster, interval_hours=None)
    assert isinstance(timesteps, list) and all(
        isinstance(step, str) for step in timesteps
    )


def test_get_raster_from_json():
    scenario = downloader.find_scenarios_by_model_slug(
        "005a58d09538e4e4cdbe48f2f3f22aeb89330ae4"
    )[0]
    raster = downloader.get_raster_from_json(scenario, "depth-max-dtri")
    assert raster["uuid"] == "4ef95627-e370-4eba-a5bc-bed661a3101a"


def test_request_json_from_url():
    url = (
        "https://demo.lizard.net/api/v3/scenarios/06c38953-31ec-4f6d-ae1f-ccdf31a348ae/"
    )
    assert isinstance(downloader.request_json_from_url(url, params=None), dict)
