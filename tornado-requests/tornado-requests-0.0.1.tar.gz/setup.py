import setuptools
from setuptools import setup

setup(name='tornado-requests',
      version='0.0.1',
      description='对tornado中AsyncHTTPClient的一个简单疯转，希望api能够向requests学习，大多数api并不改变，但是部分api变得更加方便，比如传递cookies，以及参数',
      url='https://github.com/hfldqwe/tornado-requests.git',
      author='hfldqwe',
      author_email='1941066681@qq.com',
      license='MIT',
      packages=setuptools.find_packages())
