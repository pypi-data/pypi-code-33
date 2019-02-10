from setuptools import setup

with open('./README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='map-dictionary-keys',
    version='0.0.1',
    packages=['tests', 'map_dictionary_keys'],
    url='https://github.com/melwell89/map-dictionary-keys',
    author='Matt Elwell',
    author_email='mjelwell89@gmail.com',
    description='A function to map the keys in a dictionary',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
