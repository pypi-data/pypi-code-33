from setuptools import setup, find_packages
setup(name='upylib',
      packages=find_packages(),
      version='0.4.24',
      url='https://gitlab.com',
      author='windnc',
      author_email='windnc@gmail.com',
      description='UKi\'s small libraries',
      license='MIT',
      long_description=open('README.md').read(),
      zip_safe=False,
      setup_requires=[]
      )
#python_requires  = '>=3',
#packages=find_packages(exclude=['doc', 'test*']),
