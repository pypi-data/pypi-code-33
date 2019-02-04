import os

from unittest import mock
import pytest
import redis

from skidward.backend import RedisBackend, RedisProxy, RedisDummyBackend


class TestRedisBackend:
    def test_get_expected_backend(self):
        backend = RedisBackend()
        assert backend.__class__.__name__ == "RedisProxy"
        assert backend.backend.__class__.__name__ == "RedisDummyBackend"

    @mock.patch("skidward.backend.StrictRedis")
    def test_get_actual_redis_backend(self, mock_redis):
        # TESTING env var is added via the autouse "enable_testing" fixture
        # Need to remove it to check the real case behavior
        os.environ.pop("TESTING")
        backend = RedisBackend()
        assert backend.__class__.__name__ == "RedisProxy"
        assert backend.backend.__class__.__name__ == "MagicMock"

    @mock.patch("skidward.backend.StrictRedis")
    def test_call_actual_redis_commands(self, mock_redis):
        # TESTING env var is added via the autouse "enable_testing" fixture
        # Need to remove it to check the real case behavior
        os.environ.pop("TESTING")
        backend = RedisBackend()
        backend.lpush("jobs", 1)
        backend.lrange("jobs", 0, -1)

        calls = [
            mock.call(),
            mock.call().lpush("jobs", 1),
            mock.call().lrange("jobs", 0, -1),
        ]

        assert mock_redis.mock_calls == calls


class TestRedisProxy:
    @pytest.mark.parametrize("expected_class", (RedisDummyBackend, redis.Redis))
    def test_proxy_returns_expected_class(self, expected_class):
        backend = RedisProxy(expected_class)
        assert backend.backend == expected_class


class TestRedisDummyBackend:
    @pytest.mark.parametrize("list_name, expected", (("job", True), ("nope", False)))
    def test_job_exists_in_redis_list(self, list_name, expected):
        dummy_backend = RedisDummyBackend()
        assert not dummy_backend.job_exists(list_name)
        dummy_backend.redis_lists["job"] = [1]
        assert dummy_backend.job_exists(list_name) is expected

    @pytest.mark.parametrize("jobs_id", (2, [2]))
    def test_lpush_handles_int_and_list(self, jobs_id):
        dummy_backend = RedisDummyBackend()
        dummy_backend.redis_lists["job"] = ["1".encode("utf-8")]

        dummy_backend.lpush("job", jobs_id)

        assert dummy_backend.redis_lists["job"] == [
            "2".encode("utf-8"),
            "1".encode("utf-8"),
        ]

    @pytest.mark.parametrize("list_name", ("job", "add_me"))
    def test_lpush_creates_redis_list_if_not_existing(self, list_name):
        dummy_backend = RedisDummyBackend()
        assert not dummy_backend.redis_lists

        dummy_backend.lpush(list_name, 1)

        assert dummy_backend.redis_lists
        jobs = dummy_backend.redis_lists.keys()
        assert list(jobs)[0] == list_name

    @pytest.mark.parametrize("values", ([1], [1, 2], [1, 2, 3]))
    def test_lrange_on_an_existing_job_returns_values(self, values):
        dummy_backend = RedisDummyBackend()
        assert not dummy_backend.lrange("job", 0, -1)
        dummy_backend.redis_lists["job"] = values

        result = dummy_backend.lrange("job", 0, -1)

        assert values == result

    @pytest.mark.parametrize(
        "start, end, expected",
        ((0, -1, [1, 2, 3, 4, 5]), (0, 3, [1, 2, 3, 4]), (1, 3, [2, 3, 4])),
    )
    def test_lrange_returns_expected_segment(self, start, end, expected):
        dummy_backend = RedisDummyBackend()
        assert not dummy_backend.lrange("job", start, end)
        dummy_backend.redis_lists["job"] = [1, 2, 3, 4, 5]

        result = dummy_backend.lrange("job", start, end)

        assert result == expected

    @pytest.mark.parametrize(
        "start, end, expected",
        (
            (-10, 0, [1]),
            (-10, 10, [1, 2, 3, 4, 5]),
            (0, -10, []),
            (6, 10, []),
            (4, 2, []),
        ),
    )
    def test_lrange_when_start_end_are_out_of_bounds(self, start, end, expected):
        dummy_backend = RedisDummyBackend()
        assert not dummy_backend.lrange("job", start, end)
        dummy_backend.redis_lists["job"] = [1, 2, 3, 4, 5]

        result = dummy_backend.lrange("job", start, end)

        assert result == expected

    def test_erase_deletes_redis_list(self):
        dummy_backend = RedisDummyBackend()
        dummy_backend.redis_lists["job"] = [1, 2, 3, 4, 5]
        assert dummy_backend.redis_lists
        dummy_backend.erase()
        assert not dummy_backend.redis_lists

    def test_exception(self):
        dummy_backend = RedisDummyBackend()
        with pytest.raises(AttributeError) as attr_error:
            dummy_backend.fake_function()
        assert "'RedisDummyBackend' object has no attribute 'fake_function'" == str(
            attr_error.value
        )
