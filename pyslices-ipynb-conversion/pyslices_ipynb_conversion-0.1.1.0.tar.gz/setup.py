from distutils.core import setup

# Read the version number
with open("pyslices_ipynb_conversion/_version.py") as f:
    exec(f.read())

setup(
    name='pyslices_ipynb_conversion',
    version=__version__, # use the same version that's in _version.py
    author='David N. Mashburn',
    author_email='david.n.mashburn@gmail.com',
    packages=['pyslices_ipynb_conversion'],
    scripts=[],
    url='http://pypi.python.org/pypi/pyslices_ipynb_conversion/',
    license='LICENSE.txt',
    description='conversion functions between pyslices and ipynb files',
    long_description=open('README.txt').read(),
    install_requires=[
                      'nbformat'>=4.0,
                     ],
)
