from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pysumo',
      version='0.6',
      description='Control your parrot jumping Sumo!',
      author='DEFRETIERE Clement',
      author_email='pysumo@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      include_package_data=True,
      license='MIT',
      packages=find_packages(),
      install_requires=[
            'python-socketio'
          ]
      )
