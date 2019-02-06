from setuptools import setup,find_packages

#vers='0.1.16'

setup(name='clarus',
      version='0.1.44',
      description='Clarus Microservices',
      url='http://www.clarusft.com',
      author='Clarus Financial Technology',
      author_email='support@clarusft.com',
      #packages=['clarus','clarus.services'],
      packages=find_packages(exclude=["test","clarusui"]), # <- test is excluded
      install_requires=[
          'requests','six'
      ],
      zip_safe=False)