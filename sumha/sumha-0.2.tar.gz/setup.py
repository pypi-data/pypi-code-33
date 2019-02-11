from setuptools import setup

setup(name='sumha',
      test_suite='nose.collector',
      tests_require=['nose'],
      version='0.1',
      description='The sumha...',
      long_description='Really, the sumha around.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='sumha joke comedy flying circus',
      url='http://github.com/storborg/sumha',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['sumha'],
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)
