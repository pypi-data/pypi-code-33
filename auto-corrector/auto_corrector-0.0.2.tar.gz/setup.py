from setuptools import setup, find_packages

version = '0.0.2'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='auto_corrector',
      version=version,
      description="English language spelling corrector",
      long_description=long_description,
      classifiers=[
          'Natural Language :: English',
          'Topic :: Text Processing :: Linguistic',
          'License :: OSI Approved :: MIT License'
      ],
      keywords='Natural language spelling corrector',
      author='Akhil Kumar D',
      author_email='akhilkumar.doppalapudi@gmail.com',
      url='https://github.com/akhilkumard/auto_corrector',
      license='MIT',
      package_data={'': ['big.txt','en_US_GB_CA_lower.txt','en_US_GB_CA_mixed.txt','Global_dict.txt']},
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data = True,
      zip_safe=False
      )
