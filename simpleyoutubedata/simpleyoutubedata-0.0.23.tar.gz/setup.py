import setuptools
import re

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('youtube/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name="simpleyoutubedata",
                author="Katistic",
                url="https://github.com/Katistic/Simple-Youtube-Data",
                version=version,
                packages=setuptools.find_packages(),
                license="MIT",
                description="The Youtube Data API but simplified",
                long_description=long_description,
                include_package_data=True,
                install_requires=requirements,
                classifiers=[
                    "Programming Language :: Python :: 3",
                    "License :: OSI Approved :: MIT License",
                    "Natural Language :: English",
                    "Operating System :: OS Independent",
                ])
