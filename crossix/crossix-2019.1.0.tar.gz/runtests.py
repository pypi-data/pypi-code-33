#!/usr/bin/env python
import sys
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'dev.db',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.sessions',
            'django.contrib.staticfiles',
            'crossix',
        ],
        STATIC_ROOT='/tmp/crossix_test_static/',
        STATIC_URL='/static/',
        ROOT_URLCONF='crossix.urls',
    )

def runtests(*test_args):
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests(['crossix', ])
    if failures:
        sys.exit(failures)

if __name__ == '__main__':
    runtests(*sys.argv[1:])
