# coding: UTF-8

import errno
from ctypes import c_long, c_uint, pointer

import unittest

from linux_aio_bind import IOEvent, aio_context_t, io_destroy, io_getevents, io_setup, io_submit, iocb_p


class TestContext(unittest.TestCase):
    def test_ctx_setup(self):
        ctx = aio_context_t()
        io_setup(c_uint(10), pointer(ctx))
        self.assertNotEqual(0, ctx.value)

        io_destroy(ctx)

    def test_exceed_max_nr(self):
        with open('/proc/sys/fs/aio-max-nr') as fp:
            max_nr = int(fp.read())

        with self.assertRaises(OSError) as assertion:
            ctx = aio_context_t()
            io_setup(c_uint(max_nr + 1), pointer(ctx))
            self.assertNotEqual(0, ctx.value)

            io_destroy(ctx)

        self.assertEqual(errno.EAGAIN, assertion.exception.errno)

    def test_empty_submit(self):
        ctx = aio_context_t()
        io_setup(c_uint(10), pointer(ctx))
        self.assertNotEqual(0, ctx.value)

        ret = io_submit(ctx, c_long(0), (iocb_p * 0)())
        self.assertEqual(0, ret)

        io_destroy(ctx)

    def test_empty_getevents(self):
        ctx = aio_context_t()
        io_setup(c_uint(10), pointer(ctx))
        self.assertNotEqual(0, ctx.value)

        ret = io_getevents(ctx, c_long(0), c_long(100), (IOEvent * 0)(), None)
        self.assertEqual(0, ret)

        io_destroy(ctx)

    def test_empty_submit_n_getevents(self):
        ctx = aio_context_t()
        io_setup(c_uint(10), pointer(ctx))
        self.assertNotEqual(0, ctx.value)

        ret = io_submit(ctx, c_long(0), (iocb_p * 0)())
        self.assertEqual(0, ret)

        ret = io_getevents(ctx, c_long(0), c_long(100), (IOEvent * 0)(), None)
        self.assertEqual(0, ret)

        io_destroy(ctx)


if __name__ == '__main__':
    unittest.main()
