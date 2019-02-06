import setuptools
#If there is no __init__.py in pkg1 directory, it won't be identified as package
#setup tools will not included it in the distribution

setuptools.setup(
    name="pkg-examples",
    version="0.1",
    author="madhusudanan kandasamy",
    author_email="madhukandasamy@yahoo.com",
    description="A small example package",
    url="https://github.com/kmadhugit/pkg_example.git",
    packages=setuptools.find_packages(),
    install_requires = [
        'flask'
        ]
)
