# -*- coding: utf-8 -*-
"""The downloader part of the threedi_scenario_downloader supplies the user with often used functionality to look up and export 3Di results using the Lizard API"""
import requests
from urllib.parse import urlparse
from time import sleep
import logging
import os

LIZARD_URL = "https://demo.lizard.net/api/v3/"
RESULT_LIMIT = 10
REQUESTS_HEADERS = {}

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def get_headers():
    """return headers"""

    return REQUESTS_HEADERS


def set_headers(username, password):
    """set Lizard login credentials"""

    REQUESTS_HEADERS["username"] = username
    REQUESTS_HEADERS["password"] = password
    REQUESTS_HEADERS["Content-Type"] = "application/json"


def find_scenarios_by_model_slug(model_uuid, limit=RESULT_LIMIT):
    """return json containing scenarios based on model slug"""

    url = "{}scenarios/".format(LIZARD_URL)
    payload = {"model_name__icontains": model_uuid, "limit": limit}
    r = requests.get(url=url, headers=get_headers(), params=payload)
    r.raise_for_status()
    return r.json()["results"]


def find_scenarios_by_name(name, limit=RESULT_LIMIT):
    """return json containing scenarios based on name"""
    url = "{}scenarios/".format(LIZARD_URL)
    payload = {"name__icontains": name, "limit": limit}
    r = requests.get(url=url, headers=get_headers(), params=payload)
    r.raise_for_status()
    return r.json()["results"]


def get_netcdf_link(scenario_uuid):
    """return url to raw 3Di results"""
    r = requests.get(
        url="{}scenarios/{}".format(LIZARD_URL, scenario_uuid), headers=get_headers()
    )
    r.raise_for_status()
    for result in r.json()["result_set"]:
        if result["result_type"]["code"] == "results-3di":
            url = result["attachment_url"]
            return url


def get_aggregation_netcdf_link(scenario_uuid):
    """return url to raw 3Di results"""
    r = requests.get(
        url="{}scenarios/{}".format(LIZARD_URL, scenario_uuid), headers=get_headers()
    )
    r.raise_for_status()
    for result in r.json()["result_set"]:
        if result["result_type"]["code"] == "aggregate-results-3di":
            url = result["attachment_url"]
            return url


def get_gridadmin_link(scenario_uuid):
    """return url to gridadministration"""
    r = requests.get(
        url="{}scenarios/{}".format(LIZARD_URL, scenario_uuid), headers=get_headers()
    )
    r.raise_for_status()
    for result in r.json()["result_set"]:
        if result["result_type"]["code"] == "grid-admin":
            url = result["attachment_url"]
            return url


def get_logging_link(scenario_uuid):
    """return url to zipped logging"""
    r = requests.get(
        url="{}scenarios/{}".format(LIZARD_URL, scenario_uuid), headers=get_headers()
    )
    r.raise_for_status()
    for result in r.json()["result_set"]:
        if result["result_type"]["code"] == "logfiles":
            url = result["attachment_url"]
            return url


def get_raster(scenario_uuid, raster_code):
    """return json of raster based on scenario uuid and raster type"""

    r = requests.get(
        url="{}scenarios/{}".format(LIZARD_URL, scenario_uuid), headers=get_headers()
    )
    r.raise_for_status()
    for result in r.json()["result_set"]:
        if result["result_type"]["code"] == raster_code:
            return result["raster"]


def create_raster_task(raster, target_srs, resolution, bounds=None, time=None):
    """create Lizard raster task"""

    if bounds == None:
        bounds = raster["spatial_bounds"]

    e = bounds["east"]
    w = bounds["west"]
    n = bounds["north"]
    s = bounds["south"]

    source_srs = "EPSG:4326"

    bbox = "POLYGON(({} {},{} {},{} {},{} {},{} {}))".format(
        w, n, e, n, e, s, w, s, w, n
    )

    url = "{}rasters/{}/data/".format(LIZARD_URL, raster["uuid"])
    if time is None:
        # non temporal raster
        payload = {
            "cellsize": resolution,
            "geom": bbox,
            "srs": source_srs,
            "target_srs": target_srs,
            "format": "geotiff",
            "async": "true",
        }
    else:
        # temporal rasters
        payload = {
            "cellsize": resolution,
            "geom": bbox,
            "srs": source_srs,
            "target_srs": target_srs,
            "time": time,
            "format": "geotiff",
            "async": "true",
        }
    r = requests.get(url=url, headers=get_headers(), params=payload)
    r.raise_for_status()
    return r.json()


# From here untested methods are added
def get_task_status(task_uuid):
    """return status of task"""
    url = "{}tasks/{}/".format(LIZARD_URL, task_uuid)
    r = requests.get(url=url, headers=get_headers())
    r.raise_for_status()
    return r.json()["task_status"]


def get_task_download_url(task_uuid):
    """return url of successful task"""
    if get_task_status(task_uuid) == "SUCCESS":
        url = "{}tasks/{}/".format(LIZARD_URL, task_uuid)
        r = requests.get(url=url, headers=get_headers())
        r.raise_for_status()
        return r.json()["result_url"]
    # What to do if task is not a success?


def download_file(url, path):
    """download url to specified path"""
    logging.debug("Start downloading file: {}".format(url))
    r = requests.get(url, auth=(get_headers()["username"], get_headers()["password"]))
    r.raise_for_status()
    with open(path, "wb") as file:
        for chunk in r.iter_content(100000):
            file.write(chunk)


def download_task(task_uuid, pathname=None):
    """download result of successful task"""
    if get_task_status(task_uuid) == "SUCCESS":
        download_url = get_task_download_url(task_uuid)
        if pathname is None:

            logging.debug("download_url: {}".format(download_url))
            logging.debug("urlparse(download_url): {}".format(urlparse(download_url)))
            pathname = os.path.basename(urlparse(download_url).path)
            logging.debug(pathname)
        download_file(download_url, pathname)


def download_raster(
    scenario_uuid,
    raster_code,
    target_srs,
    resolution,
    bounds=None,
    time=None,
    pathname=None,
):
    """
    download raster
    """
    raster = get_raster(scenario_uuid, raster_code)
    task = create_raster_task(raster, target_srs, resolution, bounds, time)
    task_uuid = task["task_id"]

    log.debug("Start waiting for task {} to finish".format(task_uuid))
    while get_task_status(task_uuid) == "PENDING":
        sleep(5)
        log.debug("Still waiting for task {}".format(task_uuid))

    if get_task_status(task_uuid) == "SUCCESS":
        # task is a succes, return download url
        log.debug(
            "Task succeeded, start downloading url: {}".format(
                get_task_download_url(task_uuid)
            )
        )
        print(
            "Task succeeded, start downloading url: {}".format(
                get_task_download_url(task_uuid)
            )
        )
        download_task(task_uuid, pathname)
    else:
        log.debug("Task failed")


def download_maximum_waterdepth_raster(
    scenario_uuid, target_srs, resolution, bounds=None, pathname=None
):
    """download Maximum waterdepth raster"""
    download_raster(
        scenario_uuid, "depth-max-dtri", target_srs, resolution, bounds, None, pathname
    )


def download_maximum_waterlevel_raster(
    scenario_uuid, target_srs, resolution, bounds=None, pathname=None
):
    """download Maximum waterdepth raster"""
    download_raster(
        scenario_uuid, "s1-max-dtri", target_srs, resolution, bounds, None, pathname
    )


def download_total_damage_raster(
    scenario_uuid, target_srs, resolution, bounds=None, pathname=None
):
    """download Total Damage raster"""
    download_raster(
        scenario_uuid, "total_damage", target_srs, resolution, bounds, None, pathname
    )


def download_waterdepth_raster(
    scenario_uuid, target_srs, resolution, time, bounds=None, pathname=None
):
    """download snapshot of Waterdepth raster"""
    download_raster(
        scenario_uuid,
        "depth-dtri",
        target_srs,
        resolution,
        bounds=bounds,
        time=time,
        pathname=pathname,
    )


def download_waterlevel_raster(
    scenario_uuid, target_srs, resolution, time, bounds=None, pathname=None
):
    """download snapshot of Waterdepth raster"""
    download_raster(
        scenario_uuid,
        "s1-dtri",
        target_srs,
        resolution,
        bounds=bounds,
        time=time,
        pathname=pathname,
    )


def download_precipitation_raster(
    scenario_uuid, target_srs, resolution, time, bounds=None, pathname=None
):
    """download snapshot of Waterdepth raster"""
    download_raster(
        scenario_uuid,
        "rain-quad",
        target_srs,
        resolution,
        bounds=bounds,
        time=time,
        pathname=pathname,
    )


def download_raw_results(scenario_uuid, pathname=None):
    url = get_netcdf_link(scenario_uuid)
    logging.debug("Start downloading raw results: {}".format(url))
    download_file(url, pathname)


def download_grid_administration(scenario_uuid, pathname=None):
    url = get_gridadmin_link(scenario_uuid)
    logging.debug("Start downloading grid administration: {}".format(url))
    download_file(url, pathname)


def clear_inbox():
    """delete all messages from Lizard inbox"""
    url = "{}inbox/".format(LIZARD_URL)
    r = requests.get(
        url=url, headers=get_headers(), params={"limit": RESULT_LIMIT}, timeout=10
    )
    r.raise_for_status()
    messages = r.json()["results"]
    for msg in messages:
        msg_id = msg["id"]
        read_url = "{}inbox/{}/read/".format(LIZARD_URL, msg_id)
        r = requests.post(url=read_url, headers=get_headers(), timeout=10)
    return True
