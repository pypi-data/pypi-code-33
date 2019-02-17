from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

install_requirements = [
    "bs4>=0.0.1",
    "Click>=5.0",
    "libvirt-python>=4.0",
    "requests>=2.20",
    "ruamel.yaml~=0.15",
]

setup_requirements = ["setuptools_scm"]

setup(
    name="vmbox",
    version="0.1.1",
    url="https://gitlab.com/digitronik/miqbox",
    license="GPLv2",
    author="Nikhil Dhandre",
    author_email="nik.digitronik@live.com",
    description="Manage Virtual Machines with Cloud Images",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="vmbox",
    packages=find_packages(include=["vmbox"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    setup_requires=setup_requirements,
    install_requires=install_requirements,
    entry_points={"console_scripts": ["vmbox=vmbox.vmbox:main"]},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
)
