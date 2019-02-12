from distutils.core import setup

with open("README.md", 'r') as fh:
    long_description = fh.read()


setup(
    name='file_search',
    version='0.0.1',
    description='searching files',
    py_modules=["file_search"],
    package_dir={'':'src'},
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ismaan1998/file_search",
    author='Indrajeet Singh',
    author_email='indrajeetsinghmaan@gmail.com',

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
