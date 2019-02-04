import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'zoot',
  packages=['zoot', 'zoot.automation', 'zoot.automation.mobile', 'zoot.bdd', 'zoot.testing', 'zoot.utils'],
  version = '0.0.6',
  description = 'Web automation and REST API testing framework',
  long_description_content_type="text/markdown",
  author = 'Brent Ray',
  author_email = 'brentlamarrayjr@gmail.com',
  url = 'https://github.com/brentlamarrayjr/zoot-py',
  keywords = ['testing', 'api', 'json', 'validation','automation','framework'],
  classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'zoot = zoot.bdd.main:main',
        ],
    },
)