from unittest import mock
import pytest

import skidward.jobs_handler.jobs_handler_process as jh
from skidward import JobStatus


class TestJobsHandlerProcess:
    @pytest.mark.parametrize("id, expected", [(1, True), (2, False)])
    def test_function_job_exists_return_if_job_present_in_redis_list(
        self, id, expected, backend
    ):
        exist = jh.job_exists(id, backend)

        assert exist is expected

    def test_adding_a_job_calls_redis(self, session, backend):
        result = backend.lrange("jobs", 0, 1)
        assert result[0] == "1".encode("utf-8")

        jh.add_jobs_to_redis(backend, [2], session)

        results = backend.lrange("jobs", 0, 1)
        assert results[0] == "2".encode("utf-8")
        assert session.query.call_count == 2
        assert session.query().filter.call_count == 1
        session.commit.assert_called_once()

    @mock.patch("skidward.jobs_handler.jobs_handler_process.db")
    def test_getting_a_job_when_it_is_ready(
        self, mock_db, session, backend, add_job_to_db
    ):
        assert not jh.get_jobs(backend)
        add_job_to_db(2, JobStatus.READY)
        mock_db.session = session

        jh.get_jobs(backend)

        results = backend.lrange("jobs", 0, -1)
        assert len(results) == 2
        assert results[0] == "2".encode("utf-8")
        assert session.query.call_count == 3
        assert session.query().filter.call_count == 2
        session.commit.assert_called_once()

    @mock.patch("skidward.jobs_handler.jobs_handler_process.db")
    def test_getting_no_job_when_not_ready(self, mock_db, session, backend):
        assert not jh.get_jobs(backend)
        session.query().filter.return_value = []
        mock_db.session = session

        jh.get_jobs(backend)

        # Check there is only an already existing job present in the list
        results = backend.lrange("jobs", 0, -1)
        assert len(results) == 1
        assert results[0] == "1".encode("utf-8")
        assert session.query.call_count == 3
