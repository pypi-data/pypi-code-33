import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='bzflag-networking',
    version='1.0.1',
    author='Vladimir "allejo" Jimenez',
    author_email='me@allejo.io',
    description='A Python library for reading and unpacking BZFlag network packets',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/allejo/bzflag-networking.py',
    packages=setuptools.find_packages(),
    classifiers={
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    },
)
