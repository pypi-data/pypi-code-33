from setuptools import setup
from os import path
import metadata

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name='TARBSengine',
    version=metadata.version,
    packages=[''],
    url='https://github.com/tman540/T.A.R.B.S.-Engine',
    license='MIT',
    author='Steve Tautonico',
    author_email='stautonico@gmail.com',
    description='Totally Accurate RPG Battle Simulation Engine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],  install_requires=["tabulate>=0.8.3", "PyGithub>=1.43.5"]

)
