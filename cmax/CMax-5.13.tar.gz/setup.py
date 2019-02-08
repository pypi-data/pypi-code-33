from setuptools import setup

from cmax import __version__

setup(name='CMax',
      version=__version__,
      description='A simple circuit simulator',
      long_description='A program for designing and simulating LTI circuits on a breadboard',
      author='6.01 Staff',
      author_email='6.01-core@mit.edu',
      url='https://sixohone.mit.edu',
      packages=['cmax', 'cmax.sims'],
      package_data={'': ['*.csim']},
      entry_points={'console_scripts': ['cmax = cmax.__main__:main']},
      install_requires=['matplotlib>=3.0,<4.0'],
      python_requires='>=3',
      license='GPLv3',
      classifiers=['License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)']
      )
