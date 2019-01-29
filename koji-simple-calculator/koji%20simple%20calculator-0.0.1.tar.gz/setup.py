import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="koji simple calculator",
    version="0.0.1",
    author="Koji Hoenselaers",
    author_email="k.hoenselaers@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/KojiHoen/koji_projects_git",
    packages=setuptools.find_packages(),
)