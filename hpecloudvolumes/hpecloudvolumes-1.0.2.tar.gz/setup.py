# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from setuptools import setup, find_packages


__version__ = '1.0.2'


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name='hpecloudvolumes',
    version=__version__,
    license='MIT',

    url='https://cloudvolumes.hpe.com',
    description="HPE CloudVolumes Python Library",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages(),

    install_requires=['docopt', 'requests', 'terminaltables'],
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest'],
    python_requires='>=3.6',

    author='HPE CloudVolumes',

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",

        "License :: OSI Approved :: MIT License",

        "Natural Language :: English",

        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",

        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    ],

    keywords='cloud volumes storage nimble hpe',

    scripts=['bin/cloudvolumes'],

    project_urls={
        'Source': 'https://github.com/nimblestorage/hpecloudvolumes',
        # 'Documentation': 'https://hpecloudvolumes.readthedocs.io/en/latest/',
    },
)
