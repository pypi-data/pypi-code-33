import setuptools, os

__version__ = None
if os.environ.get('CI_COMMIT_TAG'):
    __version__ = os.environ['CI_COMMIT_TAG']
elif os.environ.get('CI_JOB_ID'):
    __version__ = os.environ['CI_JOB_ID']
if __version__:
    with open('__version__', 'wt') as fout:
        fout.write(__version__)
if os.path.exists('__version__'):
    with open('__version__', 'rt') as fin:
        for line in fin:
            __version__ = line.strip()

with open('requirements.txt') as fin:
    required = fin.read().splitlines()
with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='statespace',
    version=__version__,
    author='noah smith',
    author_email='noahhsmith@gmail.com',
    description='state-space distributions and decisions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/noahhsmith/statespace',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': ['statespace = statespace.__main__:main']},
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
