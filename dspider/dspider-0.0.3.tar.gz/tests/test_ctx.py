# Standard Library
import asyncio

from unittest.mock import MagicMock

# Third Party Library
import pytest

# Dsipder Module
from dspider.ctx import Context, Watcher


@pytest.fixture
def stats():
    s = Context()
    s._store.update(dict(a=1, b=2, c=3))
    yield s


@pytest.mark.parametrize("key,num", [("a", 1), ("b", 2), ("c", 3)])
@pytest.mark.asyncio
async def test_get(stats, key, num):
    assert await stats.get(key) == num


@pytest.mark.parametrize("key,num", [("a", 0), ("b", 0), ("c", 0), ("d", 1)])
@pytest.mark.asyncio
async def test_set(stats, key, num):
    assert await stats.get(key, default=None) != num
    await stats.set(key, num)
    assert await stats.get(key) == num


@pytest.mark.parametrize(
    "action,key,num,expect",
    [
        ("incr", "a", 1, 2),
        ("incr", "b", 2, 4),
        ("incr", "c", 3, 6),
        ("decr", "a", 1, 0),
        ("decr", "a", 2, -1),
        ("decr", "b", 2, 0),
        ("decr", "c", 3, 0),
    ],
)
@pytest.mark.asyncio
async def test_action(stats, action, key, num, expect):
    func = getattr(stats, action)
    assert await func(key, num) == expect


@pytest.mark.asyncio
async def test_async_iterate(stats):

    async for k in stats:
        assert k == "a"
        break

    assert (await stats.get(k)) == 1


_checked = False


@pytest.fixture
@pytest.mark.asyncio
async def check():
    def changer(b: bool):
        global _checked
        _checked = b

    yield changer

    global _checked
    _checked = False


@pytest.fixture
@pytest.mark.asyncio
async def create_watcher():
    watchers = []

    def creater(checker, interval=0.001):
        watcher = Watcher(checker=checker, interval=interval)
        watchers.append(watcher)
        return watcher

    yield creater

    for watcher in watchers:
        if watcher.running:
            await watcher.stop()


@pytest.fixture
@pytest.mark.asyncio
async def watcher(create_watcher):
    w = create_watcher(checker=lambda: _checked)
    await w.start()
    yield w


@pytest.mark.asyncio
async def test_stop_not_running_watcher():
    w = Watcher(checker=lambda: False, interval=1)
    with pytest.raises(RuntimeError):
        await w.stop()


@pytest.mark.asyncio
async def test_watcher(create_watcher):
    checked = False

    def checker() -> bool:
        return checked

    w = create_watcher(checker)

    cb = MagicMock()
    await w.register(cb)
    await w.start()
    assert not cb.called

    checked = True
    await asyncio.sleep(0.1)
    assert cb.called
    assert cb.call_count > 1


@pytest.mark.asyncio
async def test_async_check_watcher(create_watcher):
    checked = False

    async def checker() -> bool:
        return checked

    w = create_watcher(checker)

    cb = MagicMock()
    await w.register(cb)
    await w.start()
    assert not cb.called

    checked = True
    await asyncio.sleep(0.1)
    assert cb.called
    assert cb.call_count > 1


@pytest.mark.asyncio
async def test_broken_checker_watcher(create_watcher, caplog):
    def checker():
        raise ValueError

    def dummy_cb():
        pass

    w = create_watcher(checker)
    await w.start()
    await w.register(dummy_cb)
    await asyncio.sleep(0.1)
    warning_logs = [
        record for record in caplog.records if record.levelname == "WARNING"
    ]
    assert len(warning_logs) > 1


@pytest.mark.asyncio
async def test_broken_cb_watcher(watcher, check, caplog):
    def broken_cb():
        raise ValueError

    await watcher.register(broken_cb)
    warning_logs = [
        record for record in caplog.records if record.levelname == "WARNING"
    ]
    assert len(warning_logs) == 0

    check(True)
    await asyncio.sleep(0.1)

    warning_logs = [
        record for record in caplog.records if record.levelname == "WARNING"
    ]
    assert len(warning_logs) > 1
