import json
import os
import sys
import time

from dateutil.parser import parse
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from urllib.request import Request, urlopen

COLLECTION_TIME = Summary("gitlab_jobs_collector_collect_seconds",
                          "Time spent to collect metrics from GitLab")

class GitLabJobsCollector:
    """gitlab jobs exporter"""
    scopes = ["failed", "success"]


    def __init__(self, url, project, token):
        """initalize target and project for collector"""
        self._url = url.rstrip("/")
        self._project = project
        self._token = token
        self._prometheus_metrics = {}


    def collect(self):
        """collect interface used by REGISTRY"""
        start = time.time()

        self._setup_prometheus_metrics()

        for scope in self.scopes:
            latest = self._request_data(scope)
            self._add_to_prometheus_metrics(scope, latest)

        for scope in self.scopes:
            for metric in self._prometheus_metrics[scope].values():
                yield metric

        duration = time.time() - start
        COLLECTION_TIME.observe(duration)


    def _setup_prometheus_metrics(self):
        """setup metrics we want to export"""
        for scope in self.scopes:
            self._prometheus_metrics[scope] = {
                "id":
                    GaugeMetricFamily("gitlab_job_id",
                                      "GitLab job id",
                                      labels=["project", "scope"]),
                "duration":
                    GaugeMetricFamily("gitlab_job_duration_seconds",
                                      "GitLab job duration in seconds",
                                      labels=["project", "scope"]),
                "startingDuration":
                    GaugeMetricFamily("gitlab_job_starting_duration_seconds",
                                      "GitLab job starting duration in seconds",
                                      labels=["project", "scope"]),
                "totalDuration":
                    GaugeMetricFamily("gitlab_job_total_duration_seconds",
                                      "GitLab job total duration in seconds",
                                      labels=["project", "scope"]),
                "timestamp":
                    GaugeMetricFamily("gitlab_job_timestamp_seconds",
                                      "GitLab job finish timestamp in unixtime",
                                      labels=["project", "scope"]),
            }


    def _request_data(self, scope):
        """request jobs from gitlab for a scope"""
        request = Request(
            "{0}/api/v4/projects/{1}/jobs?scope[]={2}".format(
                self._url, self._project, scope))
        request.add_header("PRIVATE-TOKEN", self._token)

        # latest job is always the first item
        return json.loads(urlopen(request).read().decode("utf-8"))[0]


    def _add_to_prometheus_metrics(self, scope, data):
        """add compute data and scope for prometheus_metrics"""
        self._prometheus_metrics[scope]["id"].add_metric([self._project, scope], data.get("id", 0))
        self._prometheus_metrics[scope]["duration"].add_metric([self._project, scope], data.get("duration", 0))

        try:
            created = parse(data.get("created_at")).timestamp()
            started = parse(data.get("started_at")).timestamp()
            finished = parse(data.get("finished_at")).timestamp()

            # TODO what if started or finished is 0
            # shouldn't happen for scopes ["failed", "success"]
            starting = started - created
            total = finished - created
        except TypeError:
            finished = 0
            starting = 0
            total = 0
        self._prometheus_metrics[scope]["timestamp"].add_metric([self._project, scope], finished)
        self._prometheus_metrics[scope]["startingDuration"].add_metric([self._project, scope], starting)
        self._prometheus_metrics[scope]["totalDuration"].add_metric([self._project, scope], total)
