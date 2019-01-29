#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from ccc/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("ccc", "__init__.py")

if sys.argv[-1] == 'publish':
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='CCC',
    version=version,
    description="""Cloud Custom Connections""",
    long_description=readme + '\n\n' + history,
    author='Cloud Custom Solutions Team',
    author_email='team@cloudcustomsolutions.com',
    url='https://github.com/CloudPR/CCC',
    packages=[
        'ccc',
    ],
    include_package_data=True,
    install_requires=[
        'django-extensions==2.1.3',
        'django-debug-toolbar==1.11',
        'django-allauth>=0.36.0',
        'django-phonenumber-field>=2.0.0',
        'Pillow>=5.2.0',
        'django-loginas',
        'python-slugify==1.2.6',
        'pendulum',
        'premailer',
        'djangorestframework==3.8.2',
        'sorl-thumbnail',
        'django-admin-sortable',
        'stripe==2.17.0',
        'paypal',
        'paypalrestsdk',
        'django-oauth-toolkit',
        'django-anymail',
        'pydub',
        'django-annoying',
        'django-simple-history',
        'validators',
        'python-magic',
        'google-api-python-client==1.7.4',
        'google-cloud',
        'pygeoip',
        'django-embed-video',
        'django-wysiwyg-redactor',
        'simplejson',
        'django-model-utils',
        'xlrd',
        'xlwt',
        'django-widget-tweaks',
        'oauth2client',
        'pydub',
        'google-cloud-vision',
        'django-extra-views',
        'django-storages==1.7.1',
        'google-cloud-storage',
        'twilio==6.19.2',
        'psycopg2',
        'django-bootstrap3==11.0.0',
        'sentry-sdk==0.3.11',
        'phonenumbers>=7.0.2',
        'django-filter==1.1.0',
        'django-rest-swagger==2.2.0',
        'requests==2.20.1'
    ],
    zip_safe=False,
    keywords='CCC',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
