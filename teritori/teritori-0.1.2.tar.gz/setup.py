from setuptools import setup, find_packages

with open('README.rst', mode='r') as f:
    l_description = f.read()

setup(name='teritori',
      version='0.1.2',
      description='Replications origin and terminus prediction in bacterial genomes',
      long_description=l_description,
      url='https://github.com/evolegiolab/findingori2',
      author='Wiktor Gustafsson, Joakim Lindstrom, Ina Oden Osterbo',
      author_email='teritori.team@gmail.com',
      license='GNU General Public License v3 or later (G  PLv3+)',

      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      keywords='bioinformatics genomics replication',
      install_requires=[
          'biopython',
          'numpy',
          'matplotlib',
          'scipy',
          'scikit-learn',
          'bcbio-gff'
      ],
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'terITori = teritori.teritori:main',
          ]
      },
      )
