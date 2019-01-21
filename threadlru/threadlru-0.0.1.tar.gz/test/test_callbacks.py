from unittest import TestCase

from threadlru import LRUCache


class TestCallback(TestCase):
    def test_insert(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter += 1
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_insert(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 1, "Insert callback should only be called once on an insert + update."

    def test_update_default(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter = value
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_update(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 1, "Update callback should be called with old value by default."

    def test_update_new(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter = value
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_update_new(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 2, "Update callback should be called with new value."

    def test_update_old(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter = value
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_update_old(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 1, "Update callback should be called with old value."

    def test_update_count(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter += 1
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_update(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 1, "Update callback should only be called once on an insert + update."

    def test_upsert_count(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter += 1
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_upsert(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 2, "Upsert callback should be called twice on an insert + update."

    def test_upsert_default(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter = value
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_upsert(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 1, "Upsert callback should be called with old value by default."

    def test_upsert_new(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter = value
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_upsert_new(func)

        data.set(key = "cat", value = 1)
        assert test() == 1, "Upsert callback should be called the first time with the old value."

        data.set(key = "cat", value = 2)
        assert test() == 2, "Upsert callback should be called with new value."

    def test_upsert_old(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter = value
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_update_old(func)

        data.set(key = "cat", value = 1)
        data.set(key = "cat", value = 2)

        assert test() == 1, "Update callback should be called with old value."

    def test_remove(self):
        data = LRUCache(max_size = 2)

        def helper():
            counter = 0

            def h1(key, value):
                nonlocal counter
                counter += 1
                return counter

            def h2():
                nonlocal counter
                return counter

            return h1, h2

        func, test = helper()
        # This should get executed once (only on new inserts)
        data.on_remove(func)

        data.set(key = "cat", value = 1)
        data.set(key = "dog", value = 2)
        data.set(key = "mouse", value = 3)

        assert test() == 1, "Remove callback should be called once with oldest value on a pop."
