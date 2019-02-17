from unittest import mock
import pytest

from skidward import JobStatus

# import before skidward.models to avoid circular imports
from skidward import web
from skidward.backend import RedisBackend
from skidward.models import Job


@pytest.fixture(autouse=True)
def enable_testing(monkeypatch):
    monkeypatch.setenv("TESTING", "True")


class Jobs(Job):
    def __init__(self, id, state):
        self.id = id
        self.state = state


class JobGenerator:
    def __init__(self):
        self.jobs = []

    def __iter__(self):
        for job in self.jobs:
            yield job

    def update(self, *args, **kwargs):
        pass

    def append(self, job):
        self.jobs.append(job)


class SetupDummyBackend:
    def __init__(self):
        self.dummy_backend = RedisBackend()
        self.dummy_backend.lpush("jobs", 1)

        self.mock_jobs = JobGenerator()
        self.mock_jobs.append(Jobs(id=1, state=JobStatus.READY))


@pytest.fixture()
def setup_backend():
    get_backend = SetupDummyBackend()
    yield get_backend
    get_backend.dummy_backend.erase()


@pytest.fixture()
def backend(setup_backend):
    dummy_backend = setup_backend.dummy_backend
    yield dummy_backend


@pytest.fixture()
def session(setup_backend):
    mock_db = mock.Mock()
    mock_jobs = setup_backend.mock_jobs
    mock_db.query().filter.return_value = mock_jobs

    return mock_db


@pytest.fixture()
def add_job_to_db(setup_backend):
    def append_job_table(id, state):
        setup_backend.mock_jobs.append(Jobs(id, state))

    return append_job_table
