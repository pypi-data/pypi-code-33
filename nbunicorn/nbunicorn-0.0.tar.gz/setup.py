import setuptools

setuptools.setup(
  name = 'nbunicorn',
  packages = setuptools.find_packages(),
  version = '0.0',
  description = 'nbunicorn',
  long_description = 'nbunicorn',
  long_description_content_type = 'text/markdown',
  author = 'Blair Hudson',
  author_email = 'blair@nbunicorn.com',
  license = 'MIT',
  url = 'https://github.com/nbunicorn/nbunicorn', 
  download_url = '',
  keywords = ['data', 'machine', 'learning', 'science', 'algorithm', 'notebook'],
  classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"
  ],
  include_package_data=True
)