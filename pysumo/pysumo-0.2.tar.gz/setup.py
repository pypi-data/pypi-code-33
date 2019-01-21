from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pysumo',
      version='0.2',
      description='Control your parrot jumping Sumo!',
      author='DEFRETIERE Clement',
      author_email='pysumo@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      packages=find_packages()
      )
