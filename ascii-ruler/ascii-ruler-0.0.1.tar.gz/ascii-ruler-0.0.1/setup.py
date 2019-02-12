from setuptools import setup
setup(
    name='ascii-ruler',
    version='0.0.1',
	author="Blake Nedved",
	author_email="blakeanedved@gmail.com",
	description="A terminal based ruler for displaying the length of a file, primarily used for codegolfing",
	url="https://github.com/blakeanedved/ascii-ruler",
    entry_points={
        'console_scripts': [
            'ascii-ruler=__init__:main'
        ]
    }
)
