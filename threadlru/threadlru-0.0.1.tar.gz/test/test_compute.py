from unittest import TestCase
from threadlru import LRUCache


class TestCompute(TestCase):
    def setUp(self):
        self._data = LRUCache(max_size = 2)

    def test_compute_and_set(self):
        def helper():
            counter = 0

            def h1():
                nonlocal counter
                counter += 1
                return counter

            return h1

        # Everytime we call this function, the value changes, so we know it's not being recomputed.
        func = helper()
        my_accessor = self._data.compute_and_set_accessor(fun = func)
        my_accessor(key = "cat")
        x = self._data.get("cat")
        assert x == 1, "Incorrect returned value"

    def test_compute_in_not_exists(self):
        def helper():
            counter = 0

            def h1():
                nonlocal counter
                counter += 1
                return counter

            return h1

        # Everytime we call this function, the value changes, so we know it's not being recomputed.
        func = helper()
        self._data.compute_if_not_exists(key = "cat", fun = func)
        self._data.compute_if_not_exists(key = "cat", fun = func)
        x = self._data.get("cat")
        assert x == 1, "Function got recomputed."

    def test_compute_in_not_exists_accessor(self):
        def helper():
            counter = 0

            def h1():
                nonlocal counter
                counter += 1
                return counter

            return h1

        # Everytime we call this function, the value changes, so we know it's not being recomputed.
        func = helper()
        my_accessor = self._data.compute_if_not_exists_accessor(fun = func)
        my_accessor(key = "cat")
        my_accessor(key = "cat")
        x = self._data.get("cat")
        assert x == 1, "Function got recomputed."

    def test_compute_if_not_value(self):
        def helper():
            counter = 0

            def h1():
                nonlocal counter
                counter += 1
                return counter

            return h1

        # Everytime we call this function, the value changes, so we know it's not being recomputed.
        func = helper()
        self._data.compute_if_not_exists(key = "cat", fun = func)  # val = 1
        self._data.compute_if_not_value(key = "cat", fun = func, value = 2)  # It should compute
        self._data.compute_if_not_value(key = "cat", fun = func, value = 2)  # It should not compute
        x = self._data.get("cat")

        assert x == 2, "Function got recomputed."

    def test_compute_if_not_value_accessor(self):
        def helper():
            counter = 0

            def h1():
                nonlocal counter
                counter += 1
                return counter

            return h1

        # Everytime we call this function, the value changes, so we know it's not being recomputed.
        func = helper()

        # Here we store the value of stored_value (which is an optional parameter), and can be overridden with `value`
        # when calling our accessor.
        compute_accessor = self._data.compute_if_not_value_accessor(fun = func, stored_value = 2)
        self._data.compute_if_not_exists(key = "cat", fun = func)  # val = 1
        compute_accessor(key = "cat")  # It should compute
        compute_accessor(key = "cat")  # It should not compute
        x = self._data.get("cat")

        assert x == 2, "Function got recomputed."
