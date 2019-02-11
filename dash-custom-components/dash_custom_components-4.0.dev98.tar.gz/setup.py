import json
import os
from setuptools import setup
from version import __version__

package_name = "dash_custom_components"
author="Martin Rode"
description = "Some description"
license = "BSD"

setup(
    name=package_name,
    version=__version__,
    author=author,
    packages=[package_name],
    include_package_data=True,
    license=license,
    description=description,
    install_requires=[]
)
