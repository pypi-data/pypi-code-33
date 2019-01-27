from setuptools import setup, find_packages

# DO_NOT_MODIFY_THIS_VALUE_IS_SET_BY_THE_BUILD_MACHINE
VERSION = "1.6.0"


def readme():
    with open("README.md") as f:
        return f.read()


with open("requirements.txt") as file:
    REQUIRED_MODULES = [line.strip() for line in file]

with open("requirements-dev.txt") as file:
    DEVELOPMENT_MODULES = [line.strip() for line in file]


setup(
    name="mathtastic",
    version=VERSION,
    description="making math fantastic",
    long_description=readme(),
    keywords="math",
    url="https://github.com/justindujardin/mathtastic",
    author="Justin DuJardin",
    author_email="justin@dujardinconsulting.com",
    packages=find_packages(),
    install_requires=REQUIRED_MODULES,
    extras_require={"dev": DEVELOPMENT_MODULES},
    include_package_data=True,
)
