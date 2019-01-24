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
    return REQUESTS_HEADERS


def set_headers(username, password):
    REQUESTS_HEADERS["username"] = username
    REQUESTS_HEADERS["password"] = password
    REQUESTS_HEADERS["Content-Type"] = "application/json"


def find_scenarios_by_model_slug(model_uuid):
    """Find all 3Di scenario's produced by the supplied model. User needs to be authorized to view the model results."""
    url = "{}scenarios/?model_name__icontains={}&limit={}".format(
        LIZARD_URL, model_uuid, RESULT_LIMIT
    )
    r = requests.get(url=url, headers=get_headers())
    r.raise_for_status()
    return r.json()["results"]


def find_scenarios_by_name(name):
    """Find all 3Di scenario's matching the supplied name that the user is authorized for"""
    url = "{}scenarios/?name__icontains={}&limit={}".format(
        LIZARD_URL, name, RESULT_LIMIT
    )
    r = requests.get(url=url, headers=get_headers())
    r.raise_for_status()
    return r.json()["results"]


def get_netcdf_link(scenario_uuid):
    """Returns the link to the netcdf file of the supplied scenario"""
    r = requests.get(
        url="{}scenarios/{}".format(LIZARD_URL, scenario_uuid), headers=get_headers()
    )
    r.raise_for_status()
    for result in r.json()["result_set"]:
        if result["result_type"]["code"] == "results-3di":
            url = result["attachment_url"]
            return url


def get_raster(scenario_uuid, raster_code):
    """Returns the raster json object given the scenario-uuid and the requested raster type"""
    r = requests.get(
        url="{}scenarios/{}".format(LIZARD_URL, scenario_uuid), headers=get_headers()
    )
    r.raise_for_status()
    for result in r.json()["result_set"]:
        if result["result_type"]["code"] == raster_code:
            return result["raster"]


def create_raster_task(raster, target_srs, resolution, bounds=None, time=None):
    """
    Create a task on the Lizard server to prepare a raster with given SRS and resolution
    Full extent will be used if the bounds are not supplied
    
    """
    if bounds == None:
        bounds = raster["spatial_bounds"]

    e = bounds["east"]
    w = bounds["west"]
    n = bounds["north"]
    s = bounds["south"]

    source_srs = "EPSG:4326"

    bbox = "POLYGON+(({}+{},{}+{},{}+{},{}+{},{}+{}))".format(
        w, n, e, n, e, s, w, s, w, n
    )

    if time is None:
        # non temporal raster
        url = "{}rasters/{}/data/?cellsize={}&geom={}&srs={}&target_srs={}&format=geotiff&async=true".format(
            LIZARD_URL, raster["uuid"], resolution, bbox, source_srs, target_srs
        )
    else:
        # temporal rasters
        url = "{}rasters/{}/data/?cellsize={}&geom={}&srs={}&target_srs={}&time={}&format=geotiff&async=true".format(
            LIZARD_URL, raster["uuid"], resolution, bbox, source_srs, target_srs, time
        )
    r = requests.get(url=url, headers=get_headers())
    r.raise_for_status()
    return r.json()


# From here untested methods are added
def get_task_status(task_uuid):
    """Returns either SUCCES, PENDING or .......?"""
    url = "{}tasks/{}/".format(LIZARD_URL, task_uuid)
    r = requests.get(url=url, headers=get_headers())
    r.raise_for_status()
    return r.json()["task_status"]


def get_task_download_url(task_uuid):
    """In case the task is a succes, return the url to the file in order to download"""
    if get_task_status(task_uuid) == "SUCCESS":
        url = "{}tasks/{}/".format(LIZARD_URL, task_uuid)
        r = requests.get(url=url, headers=get_headers())
        r.raise_for_status()
        return r.json()["result_url"]
    # What to do if task is not a success?


def download_file(url, path):
    """
    Download a file (url) to the specified path
    Example: download_file(http://whatever.com/file.txt,os.path.normpath('somefolder/somefile.txt')) 
    """
    r = requests.get(url)
    r.raise_for_status()
    with open(path, "wb") as file:
        for chunk in r.iter_content(100000):
            file.write(chunk)


def download_task(task_uuid, pathname=None):
    """
    Seaches for url belonging to task_uuid and downloads this file to the specified filelocation and name.
    If no pathname is supplied the url path will be used as a relative path to store the data.
    """
    if get_task_status(task_uuid) == "SUCCESS":
        download_url = get_task_download_url(task_uuid)
        if pathname == None:
            pathname = os.path.basename(urlparse(download_url).path)
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
    Method looks up the maximum waterdepth raster based on scenario_uuid, creates a task and downloads task when succesfull
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
    """Complete procedure to download a 3Di maximum waterdepth raster"""
    download_raster(
        scenario_uuid, "depth-max-dtri", target_srs, resolution, bounds, None, pathname
    )


def download_total_damage_raster(
    scenario_uuid, target_srs, resolution, bounds=None, pathname=None
):
    """Complete procedure to download a 3Di total damage raster"""
    download_raster(
        scenario_uuid, "3di_damage", target_srs, resolution, bounds, None, pathname
    )


def download_waterdepth_raster(
    scenario_uuid, target_srs, resolution, time, bounds=None, pathname=None
):
    """Complete procedure to download a snapshot of a temporal 3Di waterdepth raster"""
    download_raster(
        scenario_uuid,
        "depth-dtri",
        target_srs,
        resolution,
        bounds=bounds,
        time=time,
        pathname=pathname,
    )


def clear_inbox():
    url = "{}inbox/".format(LIZARD_URL)
    r = requests.get(url=url, headers=get_headers())
    r.raise_for_status()
    messages = r.json()["results"]
    for msg in messages:
        msg_id = msg["id"]
        read_url = "{}inbox/{}/read/".format(LIZARD_URL, msg_id)
        r = requests.post(url=read_url, headers=get_headers())
        r.raise_for_status()
    return True
