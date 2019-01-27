class TestRunner(DiscoverRunner):
    def __init__(self, pattern=None, top_level=None, verbosity=1, interactive=True, failfast=False, **kwargs):
        super(TestRunner, self).__init__(pattern, top_level, verbosity, interactive, failfast, **kwargs)
