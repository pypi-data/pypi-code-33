import unittest
from time import sleep
from .core import *

num = 0
key = 'f'
key2 = 'fff'

def f(data):
    global num
    num = data

manager = EventManager()
manager.addListener(key, f)

class Test(unittest.TestCase):
    def setUp(self):
        manager.start()

    def tearDown(self):
        manager.stop()

    def _singleTest(self, key, n, expect, msg=''):
        manager.sendEvent(key, n)
        sleep(0.01)
        self.assertEqual(num, expect, msg=msg)

    def test_basic(self):
        self._singleTest(key, 1, 1, 'basic test')
        self._singleTest(key, 2, 2, 'basic test2')
        self._singleTest(key2, 3, 2, 'nonexist test')

    def test_stop(self):
        self._singleTest(key, 1, 1, 'basic test')

        manager.stop()
        self._singleTest(key, 2, 1, 'stop test')
        manager.start()
        sleep(0.1)
        self.assertEqual(num, 2, msg='stop test2')

    def test_clear(self):
        self._singleTest(key, 1, 1, 'basic test')

        manager.stop()
        self._singleTest(key, 2, 1, 'clear test')
        manager.clear()
        manager.start()
        sleep(0.1)
        self.assertEqual(num, 1, msg='clear test2')

    def test_remove(self):
        self._singleTest(key, 1, 1, 'basic test')

        manager.removeListener(key, f)
        self._singleTest(key, 2, 1, 'remove test')

        manager.addListener(key, f)
        self._singleTest(key, 3, 3, 'add test')

if __name__ == '__main__':
    unittest.main()
