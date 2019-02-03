# Copyright (c) 2019 bluelief.
# This source code is licensed under the MIT license.

from setuptools import setup, find_packages


entry_points = {
    'console_scripts': [
        'rapid-start = rapidrush.core:main'
    ]
}


version = __import__('rapidrush').__version__


setup(
    name="rapidrush",
    version=version,
    url='https://github.com/bluelief/rapidrush',
    author="bluelief",
    description="Python project template. Rapid start for projects.",
    license="MIT",
    keywords="python, project, template",
    packages=find_packages(),
    include_package_data=True,
    entry_points=entry_points,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Japanese'
    ],
    project_urls={
        'Github': 'https://github.com/bluelief/rapidrush',
    },
)