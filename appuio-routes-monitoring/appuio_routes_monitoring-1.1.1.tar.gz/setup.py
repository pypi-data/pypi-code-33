"""setup instructions for repository_sync"""

from setuptools import setup, find_packages
import appuio_routes_monitoring as package


def read_file(filename):
    """Fetch the contents of a file"""
    with open(filename) as file:
        return file.read()


setup(
    name='appuio_routes_monitoring',
    author=package.__author__,
    author_email=package.__email__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Systems Administration',
    ],
    description=package.__doc__.strip().split('\n')[0],
    long_description=read_file('README.rst'),
    entry_points={
        'console_scripts': [
            # pylint: disable=line-too-long
            'generate_monitoring_check = appuio_routes_monitoring.generate_monitoring_check:main'  # noqa: E501
        ]
    },
    install_requires=read_file('requirements.in').split(),
    python_requires='>=3.5',
    # BSD 3-Clause License:
    # - http://opensource.org/licenses/BSD-3-Clause
    license=package.__license__,
    packages=find_packages(exclude=['tests']),
    platforms=['any'],
    url='https://git.vshn.net/vshn/appuio_routes_monitoring',
    version=package.__version__,
)
