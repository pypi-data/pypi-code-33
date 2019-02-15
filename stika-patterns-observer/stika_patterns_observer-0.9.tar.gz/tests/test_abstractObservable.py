from stika.patterns.observer import AbstractObservable, Observer
from unittest import TestCase
from unittest.mock import create_autospec
from enum import Enum


class ValEnum(Enum):
    first = 0
    second = 1


class TestAbstractObservable(TestCase):
    def test_register(self):
        args = [123, "test", True, ValEnum.first]
        mock = create_autospec(spec=Observer, spec_set=True, instance=True)
        for arg in args:
            with self.subTest(arg=arg):
                mock.reset_mock()
                uut = AbstractObservable()
                uut.register(mock)
                uut._notify_observers(arg)
                mock.notify.assert_called_once_with(arg)

    def test_unregister(self):
        mock = create_autospec(spec=Observer, spec_set=True)
        uut = AbstractObservable()
        # Register
        uut.register(mock)
        # Unregister
        uut.unregister(mock)
        # Verify notify is never called
        uut._notify_observers(1)
        mock.notify.assert_not_called()

    def test_unregister_after_a_notify(self):
        mock = create_autospec(spec=Observer, spec_set=True)
        uut = AbstractObservable()
        # Register
        uut.register(mock)
        # Notify once
        uut._notify_observers(1)
        mock.notify.assert_called_once_with(1)
        # Unregister
        uut.unregister(mock)
        # Verify notify is still only called once from first
        uut._notify_observers(1)
        mock.notify.assert_called_once()
