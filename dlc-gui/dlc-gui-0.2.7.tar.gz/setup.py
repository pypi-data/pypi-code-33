from io import open

from setuptools import find_packages, setup

with open("src/dlc_gui/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        version = "0.0.1"

# with open('README.rst', 'r', encoding='utf-8') as f:
#     readme = f.read()

REQUIRES = ["PySide2", "ruamel.yaml", "numpy", "pandas", "tables"]

setup(
    name="dlc-gui",
    version=version,
    description="dlc-gui is a GUI written in Qt5 (PySide2) for DeepLabCut.",
    # long_description=readme,
    author="d_",
    author_email="UnicodeAlt255@gmail.com",
    maintainer="d_",
    maintainer_email="UnicodeAlt255@gmail.com",
    url="https://gitlab.com/d_/dlc-gui",
    license="LGPL",
    keywords=[""],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=REQUIRES,
    tests_require=["coverage", "pytest"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
