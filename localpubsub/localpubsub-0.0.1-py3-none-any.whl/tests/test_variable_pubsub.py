import unittest as ut
from localpubsub import VariablePub
import threading as th

class TestVariablePubsub( ut.TestCase ):

    def __producer(self, iterations, pub, wait=False):
        for i in range(iterations):
            pub.publish(i)

    def __consumer_iter(self, iterations, sub):
        for i in range(iterations):
            data = sub.get()
            if data == sub.return_on_no_data:
                continue
            else:
                self.assertIn(data, range(iterations))

    def test_get_data(self):
        pub = VariablePub()
        p_thread = th.Thread(target=self.__producer, args=(10, pub))
        sub = pub.make_sub()
        s_thread = th.Thread(target=self.__consumer_iter, args=(10, sub))
        p_thread.start()
        s_thread.start()
        p_thread.join()
        s_thread.join()
