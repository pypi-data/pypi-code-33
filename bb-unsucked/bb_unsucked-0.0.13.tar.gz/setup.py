import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bb_unsucked",
    version="0.0.13",
    author="Jeffrey McAteer",
    author_email="jeffrey.p.mcateer@outlook.com",
    description="A solution to Blackboard misery for college students and professors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git-community.cs.odu.edu/jmcateer/blackboard-unsucked",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
)
