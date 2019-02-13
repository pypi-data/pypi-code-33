from setuptools import setup, find_packages

setup(name='preprocess_icm',
      version='0.50',
      author='Servicefriend',
      author_email='dev@servicefriend.com',
      description='Preprocessing incoming messages',
      packages=find_packages(),
      classifiers=(
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      license='MIT',
      zip_safe=False
      )
