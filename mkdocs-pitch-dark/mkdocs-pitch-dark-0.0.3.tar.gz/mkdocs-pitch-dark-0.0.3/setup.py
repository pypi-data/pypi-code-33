import json
import os
import subprocess

from distutils.command.sdist import sdist as sdist_orig
from setuptools import setup, find_packages

class sdist(sdist_orig):

    def run(self):
        cwd = os.getcwd()
        subprocess.run(["mkdocs", "build", "-c", "-d", "npm"])
        subprocess.run(["rm", "npm/sitemap.xml.gz"])
        subprocess.run(["cp", "package.json", "npm"])
        subprocess.run(["cp", "-R", "pitch_dark/scss", "npm"])
        os.chdir('npm')
        subprocess.run(["npm", "pack"])
        os.chdir(cwd)
        super().run()

with open("package.json") as data:
    package = json.load(data)

setup(
    name="mkdocs-pitch-dark",
    version=package["version"],
    url=package["homepage"],
    license=package["license"],
    description=package["description"],
    author=package["author"],
    author_email=package["bugs"]["email"],
    packages=find_packages(),
    include_package_data=True,
    cmdclass={
        'sdist': sdist
    },
    entry_points={
        'mkdocs.themes': [
            'pitch-dark = pitch_dark',
        ]
    },
    zip_safe=False
)
