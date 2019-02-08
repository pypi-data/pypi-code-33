from setuptools import setup


def get_version():
    version = {}
    with open("hash-id/version.py") as fp:
        exec(fp.read(), version)
    return version['__version__']


def get_readme():
    try:
        import pypandoc
        readme_data = pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError):
        readme_data = open('README.md').read()
    return readme_data


setup(
    name = 'hash-id',
    scripts = ['hash-id/hash-id'],
    url = 'https://github.com/nadroj-isk/hash-identifier',
    version = get_version(),
    description = 'Software to identify the different types of hashes used to encrypt data and especially passwords',
    author = 'nadroj-isk',
    author_email = 'jjs@auburn.edus',
    keywords = ['hacking', 'hash', 'hash-id', 'identifier', 'md5', 'sha'],
    test_suite='tests',
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)