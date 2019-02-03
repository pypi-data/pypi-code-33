SOURCEHEADER

from setuptools import setup, find_packages


requires = ["", ""]


entry_points = {"console_scripts": ["somecommand = your.project.directory:main"]}


EXCLUDE_FROM_PACKAGES = ["None"]


version = __import__("PACKAGENAME").get_version()


setup(
    name="PACKAGENAME",
    version=version,
    author="AUTHORNAME",
    description="",
    license="MIT",
    keywords="python",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    install_requires=requires,
    entry_points=entry_points,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
