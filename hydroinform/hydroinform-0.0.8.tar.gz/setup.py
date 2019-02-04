import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()



setuptools.setup(
    name="hydroinform",
    version="0.0.8",
    author="Jan Gregersen and Jacob Gudbjerg",
    author_email="jacobgudbjerg@gmail.com",
    description="A steady-state stream model and python access to DFS-files",
    url="http://hydroinform.dk",

    packages=setuptools.find_packages(include=['hydroinform']),
    install_requires=[
        'enum34;python_version<"3.4"',
        'pyshp',
        'numpy',
        'matplotlib'
        ],
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ),
)