from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pystork',
    version='0.0.1',
    packages=['tests', 'tests.optimizers', 'pystork', 'pystork.costs', 'pystork.optimizers', 'pystork.data_generators'],
    url='https://github.com/yassineameur/pystork',
    license='MIT',
    author='Yassine Ameur',
    author_email='yassine.ameur2013@gmail.com',
    description='Deep learning library for academic use.'
)
