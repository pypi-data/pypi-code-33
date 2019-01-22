from setuptools import setup
setup(
    name = 'thindf',
    py_modules = ['thindf'],
    version = '0.2.5',
    description = 'A Python implementation of thindf data format',
    long_description = open('README.md', encoding = 'utf-8').read(),
    long_description_content_type = 'text/markdown',
    author = 'Alexander Tretyak',
    author_email = 'alextretyak@users.noreply.github.com',
    url = 'http://thindf.org',
    download_url = 'https://bitbucket.org/thindf/thindf/get/default.zip',
    license = "MIT",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
)
