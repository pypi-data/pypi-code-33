from unittest import TestCase
from threadlru import LRUCache


class TestBasic(TestCase):
    def setUp(self):
        self._data = LRUCache(max_size = 2)

    def test_set_single(self):
        self._data.set(key = "cat", value = 1)
        x = self._data.get(key = "cat")
        assert type(x) == int, "Dict returned incorrect type."
        assert x == 1, "Dict returned incorrect item."

    def test_get_empty(self):
        x = self._data.get(key = "dog")
        assert x is None, "Data returned incorrect value."

    def test_set_multiple(self):
        self._data.set(key = "cat", value = 1)
        self._data.set(key = "cat", value = 2)

        x = self._data.get(key = "cat")
        assert x == 2, "Dictionary not updating values."

    def test_set_replace(self):
        # Assuming max_size = 2
        self._data = LRUCache(max_size = 2)

        self._data.set(key = "dog", value = 1)
        self._data.set(key = "cat", value = 2)
        self._data.set(key = "mouse", value = 3)

        x = self._data.get("dog")
        y = self._data.get("cat")
        z = self._data.get("mouse")
        assert z == 3, "Newest item not in dictionary"
        assert y == 2, "Second newest item not in dictionary"
        assert x is None, "Oldest item not replaced"

    def test_contains(self):
        # Assuming max_size = 2
        self._data = LRUCache(max_size = 2)

        self._data.set(key = "dog", value = 1)
        self._data.set(key = "cat", value = 2)
        self._data.set(key = "mouse", value = 3)

        x = self._data.contains(key = "dog")
        y = self._data.contains(key = "cat")
        z = self._data.contains(key = "mouse")
        assert z, "Newest item not in dictionary"
        assert y, "Second newest item not in dictionary"
        assert not x, "Oldest item not replaced"

    def test_transaction(self):
        def helper(data: LRUCache):
            # We're in a transaction on a different thread, so we should be waiting!
            data.set(key = "dog", value = 1)
            data.set(key = "cat", value = 2)
            data.set(key = "mouse", value = 3)

        from threading import Thread
        t = Thread(target = helper, args = (self._data, ))

        dict1 = self._data
        dict1.begin_transaction()
        t.start()

        # Simulate work
        dict1.set(key = "dog", value = 2)
        dict1.set(key = "cat", value = 3)
        dict1.set(key = "mouse", value = 4)

        # Thread should still be waiting, since we're in a transaction
        assert t.is_alive(), "Thread completed work before we were done."
        assert dict1.get(key = "mouse") == 4, "The other process shouldn't have written yet."
        dict1.end_transaction()

        t.join(timeout = 10)
        assert dict1.get(key = "mouse") == 3, "Last write wins."
