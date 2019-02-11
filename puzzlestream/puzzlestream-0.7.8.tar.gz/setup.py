import os
import re
import shutil
import sys
from codecs import open  # To use a consistent encoding

from setuptools import find_packages, setup  # Prefer setuptools over distutils
from setuptools.command.install import install

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


class WindowsInstaller(install):

    def run(self):
        self.__additionalOutputs = []
        startMenuDir = os.path.expanduser(
            "~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs")

        if sys.platform == "win32":
            try:
                import win32com.client as client

                shutil.copy("./puzzlestream/icons/Puzzlestream.ico",
                            os.path.join(startMenuDir, "Puzzlestream.ico"))

                shell = client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(
                    os.path.join(startMenuDir, "Puzzlestream.lnk"))
                shortcut.Targetpath = "pythonw"
                shortcut.Arguments = "-m puzzlestream.launch"
                shortcut.IconLocation = os.path.join(
                    startMenuDir, "Puzzlestream.ico")
                shortcut.save()
                self.__additionalOutputs.append(
                    os.path.join(startMenuDir, "Puzzlestream.ico"))
                self.__additionalOutputs.append(
                    os.path.join(startMenuDir, "Puzzlestream.lnk"))
            except Exception as e:
                print(e)

        super().run()

    def get_outputs(self):
        outputs = super().get_outputs()
        outputs.extend(self.__additionalOutputs)
        return outputs


out = setup(
    name="puzzlestream",

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=re.sub('^v', '', os.popen('git describe').read().strip()),

    description="Data analysis software",
    long_description=long_description,  # this is the

    # The project's main homepage.
    url="https://puzzlestream.org",

    # Author details
    author="Nils Holle, Fabian Theissen",
    author_email="info@puzzlestream.org",

    # Choose your license
    license="MIT",

    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",

        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],

    # What does your project relate to?
    keywords="data analysis",

    packages=["puzzlestream", "puzzlestream.backend", "puzzlestream.ui"],

    package_dir={"puzzlestream": "./puzzlestream"},

    package_data={"": ["icons/*", "ui/style/*",
                       "ui/translations/*", "misc/*"]},

    data_files=[("share/icons",
                 ["puzzlestream/icons/Puzzlestream_512.png"]),
                ("share/applications",
                 ["puzzlestream/misc/Puzzlestream.desktop"])],

    # Requirements
    install_requires=requirements,

    # Puzzlestream entry point
    entry_points={
        "console_scripts": [
            "puzzlestream = puzzlestream.launch:main"
        ]
    },

    cmdclass={"install": WindowsInstaller}

)
