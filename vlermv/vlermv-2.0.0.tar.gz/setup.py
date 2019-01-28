from distutils.core import setup

extras_require = {
    's3': ['boto>=2.38.0'],
    'tests': ['pytest>=2.6.4', 'testfixtures>=4.1.2'],
}

setup(name='vlermv',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Easily dump python objects to files, and then load them back.',
      url='https://thomaslevine.com/scm/vlermv/',
      packages=[
          'vlermv', 'vlermv.serializers', 'vlermv.transformers',
          'vlermv_examples',
      ],
      install_requires=[],
      extras_require=extras_require,
      tests_require=extras_require['tests'],
      version='2.0.0',
      license='AGPL',
      entry_points = {'console_scripts': ['dadaname = vlermv.transformers.magic:cli']},
)
