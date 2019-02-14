from setuptools import setup
setup(
    name = "zml",
    packages = ["zml"],
    version = "0.9.0",
    description = "zero markup language",
    author = "Christof Hagedorn",
    author_email = "zeromage@neo.codes",
    url = "http://www.zml.org/",
    download_url = "https://pypi.python.org/pypi/zml",
    keywords = ["zml", "zero", "markup", "language", "template", "templating"],
    #install_requires = ['pyparsing', 'html5lib', 'pyyaml', 'asteval' ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
zml - zero markup language
-------------------------------------

Features
 - zero markup templates
 - clean syntax
 - extensible
 - components
 - namespaces
 - lean code

This version requires Python 3 or later.
"""
)
