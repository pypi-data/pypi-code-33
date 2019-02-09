# Standard modules
import copy
import datetime
import os

# External dependencies
import pytest

# Local modules
from .context import vigil
from vigil.watch import Watch


class TestWatchBadInput:
    """
    A class to test the Watch object.
    """

    def test_interval_negative(self):
        """
        Watch should rause ValueError with negative interval
        """
        values = (-1,
                  -999,
                  -999999999)
        for value in values:
            with pytest.raises(ValueError):
                Watch('test', 'http://www.url.example',
                      interval=datetime.timedelta(days=value))

    def test_interval_zero(self):
        """
        Watch should raise ValueError with zero interval
        """
        with pytest.raises(ValueError):
            Watch('test', 'http://www.url.example',
                  interval=datetime.timedelta(0))

    def test_tolerance_zero(self):
        """
        Watch should rause ValueError if tolerance is zero.
        """
        with pytest.raises(ValueError):
            Watch('test', 'http://www.url.example', tolerance=0)


class TestWatchMethods:
    """
    Tests methods of the Watch class.
    """

    def test_check(self, watch, event_loop):
        """
        Watch should update properly.
        """
        old = {}
        old['content'] = watch.content
        old['date'] = watch.date
        event_loop.run_until_complete(watch.check())
        assert watch.date > old['date']
        assert watch.content != old['content']
        assert watch.diff

    def test_not_enough_time_passed(self, watch, event_loop):
        """
        Changed should be None if less than inverval time has passed.
        """
        watch.date = datetime.datetime.utcnow()
        event_loop.run_until_complete(watch.check())
        assert not watch.diff

    def test_force_override_check(self, watch, event_loop):
        """
        With force option, check updates should complete
        even if not enough time has passed.
        """
        watch.date = datetime.datetime.utcnow()
        old_date = datetime.datetime.utcnow()
        event_loop.run_until_complete(watch.check(force=True))
        assert watch.date > old_date

    def test_check_site_not_changed(self, event_loop):
        """
        Change should be None when the site did not change.
        """
        watch = Watch('xml', 'http://httpbin.org/xml')
        samplefile = os.path.join('tests', 'data', 'xml')
        with open(samplefile, 'r', encoding='utf-8') as f:
            watch.content = f.read()

        event_loop.run_until_complete(watch.check())
        assert not watch.diff

    def test_eq(self, watch):
        """
        Two watch object with the same attributes should be equal.
        """
        watch1 = watch
        watch2 = copy.copy(watch)
        assert watch1 == watch2
