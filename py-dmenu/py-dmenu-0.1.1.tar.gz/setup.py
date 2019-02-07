from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='py-dmenu',
    version='0.1.1',
    description='A module to easly handle dmenu inputs with python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=['py_dmenu'],
    url='http://github.com/manuelraa/py-dmenu',
    author='Manuelraa',
    author_email='manuel@bloodycrystals.de',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
