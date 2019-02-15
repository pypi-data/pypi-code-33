import unittest

from pydantic.error_wrappers import ValidationError

from pipeline.pipeline import execution_pipeline


class TestPipelinePreAndPostValidation(unittest.TestCase):

    def test_validated_does_not_require_lists(self):
        # validated pipeline handles callables and lists of callables
        good_pipeline1 = execution_pipeline(pre=lambda x: x, post=lambda x: x)
        good_pipeline2 = execution_pipeline(pre=[lambda x: x], post=[lambda x: x])

        @good_pipeline1
        def happy_function1(): return 0

        @good_pipeline2
        def happy_function2(): return 0

        self.assertEqual(happy_function1(), 0)
        self.assertEqual(happy_function2(), 0)

    def test_pre_and_post_must_be_callable(self):
        with self.assertRaises(ValidationError):
            doomed_pipeline1 = execution_pipeline(pre=1, post=1)
        with self.assertRaises(ValidationError):
            doomed_pipeline2 = execution_pipeline(pre=[1], post=1)
        with self.assertRaises(ValidationError):
            doomed_pipeline3 = execution_pipeline(pre=[1], post=lambda x: x)


class TestPipelineErrorHandlerValidation(unittest.TestCase):

    def test_needs_handler(self):
        class BadHandler:
            exception_class = BaseException
            no_handler = None
        with self.assertRaises(ValidationError):
            doomed_pipeline = execution_pipeline(error=BadHandler())

    def test_needs_exception_class(self):
        class BadHandler:
            no_exception_class = None
            handler = lambda x: x
        with self.assertRaises(ValueError):
            doomed_pipeline = execution_pipeline(error=BadHandler())

    def test_needs_callable_handler(self):
        class BadHandler:
            exception_class = BaseException
            handler = None
        with self.assertRaises(ValidationError):
            doomed_pipeline = execution_pipeline(error=BadHandler())

    def test_needs_base_exception_child(self):
        class BadHandler:
            exception_class = None
            handler = lambda x: x
        with self.assertRaises(ValidationError):
            doomed_pipeline = execution_pipeline(error=BadHandler())

    def test_valid_handler_passes(self):
        class GoodHandler:
            exception_class = BaseException
            handler = lambda x: x
        happy_pipeline = execution_pipeline(error=GoodHandler())

    def test_valid_multi_exception_handler_passes(self):
        class GoodHandler:
            exception_classes = (BaseException, Exception)
            handler = lambda x: x
        happy_pipeline = execution_pipeline(error=GoodHandler())


class TestCacheClassValidation(unittest.TestCase):

    def test_must_implement_get(self):
        class BadCache:
            no_get = lambda x: x
            set = lambda x: x

        with self.assertRaises(NotImplementedError):
            doomed_pipeline = execution_pipeline(cache=BadCache())

    def test_must_implement_set(self):
        class BadCache:
            get = lambda x: x
            no_set = lambda x: x

        with self.assertRaises(NotImplementedError):
            doomed_pipeline = execution_pipeline(cache=BadCache())

    def test_valid_cache_passes(self):
        class GoodCache:
            get = lambda x: x
            set = lambda x: x
        happy_pipeline = execution_pipeline(cache=GoodCache())
