from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

setup(
    name='payment_corner',
    version='0.0.2',
    license='MIT',
    description="Python SDK for the Payment Corner API.",
    long_description='Python SDK for the Payment Corner API.',

    author='Hassan Barbir',
    author_email='hassan.barbir@paymentcorner.com',
    url='http://documentationapi.paymentcorner.com/#introduction',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,

    keywords=[],
    install_requires=['requests'],
    test_suite='tests'
)