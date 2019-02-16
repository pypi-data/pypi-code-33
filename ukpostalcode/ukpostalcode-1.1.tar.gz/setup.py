
try:
    from setuptools.core import setup
    setup
except ImportError:
    from distutils.core import setup
    

setup (
    name = 'ukpostalcode',
    version = '1.1',
    author = 'Jorge Quiterio',
    author_mail = 'eu@jquiterio.eu',
    py_modules = ['ukpostalcode'],
    description = 'UK Post Code Format and Validation',
    url = 'https://git.jquiterio.eu/jquiterio/ukpostalcode',
    license = open('LICENSE').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Postcode"
    ],
    long_description=open('README.md').read()
)