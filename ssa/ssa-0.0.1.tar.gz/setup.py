from setuptools import setup, find_packages
import os


# read a file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# read version
exec(read(os.path.join('ssa', 'version.py')))  # pylint: disbale=W0122


# project metadata
setup(
    name='ssa',
    version=__version__,
    description='Stochastic Simulation Algorithms',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='The SSA developers',
    author_email='yannik.schaelte@gmail.com',
    url='https://github.com/yannikschaelte/ssa',
    packages=find_packages(exclude=['doc*', 'test*']),
    install_requires=['numpy',
                      'scipy',
                      'pandas',
                      'numba'],
    tests_require=[],
    python_requires='>=3.6',
)
