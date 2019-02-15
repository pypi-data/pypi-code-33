from setuptools import setup, find_packages

setup(name='mongo_pickle',
      version='0.1.2',
      description='Schema-less Pythonic Mongo ORM',
      author='111yoav',
      author_email='111yoav@gmail.com',
      license='MIT',
      package_dir={'':'mongo_pickle'},
      packages=find_packages("mongo_pickle", exclude=["test"]),
      zip_safe=False)
