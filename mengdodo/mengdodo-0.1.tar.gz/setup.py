import setuptools

with open("README.md", "r") as fh:
      long_description = fh.read()

setuptools.setup(
      name='mengdodo',
      version='0.1',
      author='mengdodo',
      author_email='losted.dreamer@gmail.com',
      description='这里是mengdodo的描述',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://mengdodo.com',
      packages=setuptools.find_packages(),
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
)