import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='jblib',
                  version='1.5',
                  description='JustBard\'s Python Utilities',
                  author='Justin Bard',
                  author_email='JustinBard@gmail.com',
                  url='http://justbard.com',
                  py_modules=['jblib'],
                  )
