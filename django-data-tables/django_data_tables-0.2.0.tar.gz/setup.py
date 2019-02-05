import os
from setuptools import find_packages, setup

from django_data_tables import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_data_tables',
    version=__version__,
    packages=['django_data_tables', 'django_data_tables.templatetags'],
    url='https://gitlab.brolabs.de/pwach/django_data_tables',
    include_package_data=True,
    license='MIT License',
    description='Framework to create dynamic data table views in Django',
    long_description=README,
    author='Paul Wachendorf',
    author_email='paul.wachendorf@web.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['django>=2.0']
)
