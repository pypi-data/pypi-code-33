import json
import time
from dateutil.parser import parse
try:
    from urllib.request  import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

# metrics:
#
# gitlab_job_time['GitRepo','Branch','PipelineId','Job']: in seconds
# gitlab_job_running_time['GitRepo','Branch','PipelineId','Job']: in seconds
# gitlab_job_duration_time['GitRepo','Branch','PipelineId','Job']: in seconds
# gitlab_job_state['GitRepo','Branch','PipelineId','Job']: success=0, pending=1, running=2, failed=3, canceled=4,skipped=5,undefined=99

# Download data via http get
def http_get_data(url,token):
    request = Request(url)
    request.add_header('PRIVATE-TOKEN', token)
    return urlopen(request)


class GitlabJobCollector():

    def __init__(self, git_project_url, git_project_id, git_token, git_branch):
        self.git_project_url = git_project_url
        self.git_project_id = git_project_id
        self.git_token = git_token
        self.git_branch = git_branch


    def collect(self):
  
        git_project = self.git_project_url + str(self.git_project_id)
        git_project_pipeline = git_project + "/pipelines"
        git_token = self.git_token
        pipelines_monitoring_lst = []
        init_timestamp = parse("1970/01/01 00:00:00.000+01:00")
  
        gitlab_job_status_success   =  0
        gitlab_job_status_pending   =  1
        gitlab_job_status_running   =  2
        gitlab_job_status_failed    =  3
        gitlab_job_status_canceled  =  4
        gitlab_job_status_skipped   =  5
        gitlab_job_status_undefined = 99
  
        # Define metrics
        metric_pending_time = GaugeMetricFamily(
            'gitlab_job_pending_time',
            'Gitlab job time between creation and starting the pipeline.',
            labels = ['GitRepo','Branch','PipelineId','Job','Stage'])
        metric_running_time = GaugeMetricFamily(
            'gitlab_job_running_time',
            'Gitlab job time between starting and finishing the pipeline.',
            labels = ['GitRepo','Branch','PipelineId','Job','Stage'])
        metric_duration_time = GaugeMetricFamily(
            'gitlab_job_duration_time',
            'Gitlab job time between creation and finishing the pipeline.',
            labels = ['GitRepo','Branch','PipelineId','Job','Stage'])
        metric_state =  GaugeMetricFamily(
            'gitlab_job_state',
            'Gitlab job state (success=0,pending=1,running=2,failed=3,canceled=4,skipped=5,undefined=99).',
            labels = ['GitRepo','Branch','PipelineId','Job','Stage'])
  
  
        # Get somme information of project 1881
        project = json.load(http_get_data(git_project, git_token))
        project_name = project.get("name")
        project_url = project.get("http_url_to_repo")
  
        # Get all pipelines of project 1881
        pipelines = json.load(http_get_data(git_project_pipeline, git_token))
  
        # Make sure we use the last pipeline
        for pl in pipelines:
            pipeline_id = pl.get("id")
            branch = pl.get("ref")
            if branch == branch:
                pipelines_monitoring_lst.append(pipeline_id)
  
        # Sort pipeline list descending
        pipelines_monitoring_lst.sort(reverse = True)
        pipeline_latest_id = str(pipelines_monitoring_lst[0])
  
        # Get pipeline specific information, e.g. updated_at
        url_pipeline_latest = git_project_pipeline + "/" + pipeline_latest_id
        pipeline_latest_details = json.load(http_get_data(url_pipeline_latest, git_token))
        pl_updated_time = parse(pipeline_latest_details.get("updated_at"))
  
        # Get information of all jobs of that last pipeline
        url_pipeline_jobs = git_project_pipeline + "/" + pipeline_latest_id + "/jobs"
        jobs = json.load(http_get_data(url_pipeline_jobs, git_token))
        for job in jobs:
            job_id = str(job.get("id"))
            stage = job.get("stage")
            creation_time = parse(job.get("created_at"))
  
            try:
                start_time = parse(job.get("started_at"))
            except:
                start_time = init_timestamp
  
            try:
                finish_time = parse(job.get("finished_at"))
            except:
                finish_time = init_timestamp
  
            state = job.get("status")
  
            # Compute Metrics pending_time, start_time, duration_time
            # pending_time
            if start_time == init_timestamp: 
                pending_time = pl_updated_time - creation_time
            else:
                pending_time = start_time - creation_time
  
            # running_time
            if finish_time == init_timestamp and start_time == init_timestamp:
                running_time = init_timestamp
            elif finish_time == init_timestamp and start_time != init_timestamp:
                if start_time > pl_updated_time:
                    running_time = start_time - pl_updated_time
                else:
                    running_time = pl_updated_time - start_time
            else:
                running_time = finish_time - start_time
  
            # duration_time
            if finish_time == init_timestamp:
                duration_time = pl_updated_time - creation_time
            else:
                duration_time = finish_time - creation_time
  
            # Map status to int
            if state == "success":
                state_int = gitlab_job_status_success
            elif state == "pending":
                state_int = gitlab_job_status_pending
            elif state == "running":
                state_int = gitlab_job_status_running
            elif state == "failed":
                state_int = gitlab_job_status_failed
            elif state == "canceled":
                state_int = gitlab_job_status_canceled
            elif state == "skipped":
                state_int = gitlab_job_status_skipped
            else:
                state_int = gitlab_job_status_undefined
  
            # Build metrics
            metric_pending_time.add_metric([project_url,branch,pipeline_latest_id,job_id,stage],pending_time.seconds)
            metric_duration_time.add_metric([project_url,branch,pipeline_latest_id,job_id,stage],duration_time.seconds)
            metric_state.add_metric([project_url,branch,pipeline_latest_id,job_id,stage],state_int)
  
            # yield metric
            yield metric_pending_time
            yield metric_duration_time
            yield metric_state
  
            # Only yield valid running_time
            if running_time != init_timestamp:
                metric_running_time.add_metric([project_url,branch,pipeline_latest_id,job_id,stage],running_time.seconds)
                yield metric_running_time


def start_server(port, interval, git_project_url, git_project_id, git_token, git_branch):

    gitlab_job = GitlabJobCollector(git_project_url, git_project_id, git_token, git_branch)

    REGISTRY.register(gitlab_job)

    start_http_server(port)
    while True: time.sleep(interval)


