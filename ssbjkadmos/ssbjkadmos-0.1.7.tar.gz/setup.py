from setuptools import setup, find_packages


from ssbjkadmos import __version__ as version


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='ssbjkadmos',
      version=version,
      description='Supersonice Business Jet (SSBJ) tools in Python using a central data schema (XML) approach.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
      ],
      keywords='optimization agile multidisciplinary engineering aircraft design',
      url='https://bitbucket.org/imcovangent/ssbjkadmos',
      download_url='https://bitbucket.org/imcovangent/ssbjkadmos/src/master/dist/ssbjkadmos-'+version+'.tar.gzip',
      author='Imco van Gent',
      author_email='i.vangent@tudelft.nl',
      license='Apache Software License',
      packages=find_packages(),
      install_requires=[
            'kadmos>=0.8',
            'lxml',
            'numpy',
            'openlego>=1.3.1',
      ],
      include_package_data=True,
      zip_safe=False)
