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
            "a790f33c-9f9f-442a-bd7f-c00f77c37bbd",
            "EPSG:28992",
            1000,
            "2018-06-02T06:00:00Z",
            None,
            "threedi_scenario_downloader/tests/testdata/waterdepth.tif",
        )


# def test_download_raw_results():
#    downloader.download_raw_results(
#        "06c38953-31ec-4f6d-ae1f-ccdf31a348ae",
#        "threedi_scenario_downloader/tests/testdata/test.nc",
#    )
#    assert True


# def test_download_grid_administration():
#    downloader.download_grid_administration(
#        "06c38953-31ec-4f6d-ae1f-ccdf31a348ae",
#        "threedi_scenario_downloader/tests/testdata/test.h5",
#    )
#    assert True


def test_clear_inbox():
    result = downloader.clear_inbox()
    assert result
