from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pinform',
      version='0.2',
      author='Sina Rezaei',
      author_email='sinarezaei1991@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      description='Python InfluxDB ORM (OSTM)',
      url='https://github.com/sinarezaei/pinform',
      license='MIT',
      packages=['pinform'],
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      zip_safe=False)