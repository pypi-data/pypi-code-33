from distutils.core import setup

extras_require = {'tests': ['pytest>=2.6.4']}

setup(name='namedtuple_extensions',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Extend the features of namedtuple.',
      url='https://thomaslevine.com/scm/namedtuple_extensions/',
      packages=['namedtuple_extensions'],
      extras_require=extras_require,
      tests_require=extras_require['tests'],
      classifiers=[
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      version='0.0.2',
      license='AGPL',
      )
