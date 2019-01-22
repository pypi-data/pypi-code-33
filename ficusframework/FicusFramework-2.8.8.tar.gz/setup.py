import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="FicusFramework",
    version="2.8.8",

    packages=find_packages('src'),
    package_dir={'': 'src'},
    test_suite="test",

    install_requires=["flask", "flask-cors", "requests", "ec2-metadata", "dnspython", "apscheduler", "jsonpath-rw",
                      "munch","PyYaml"],

    author='sunxiang0918',
    author_email="sunxiang0918@gmail.com",
    description="A framework for Ficus by Python3.",
    long_description=read("README.rst"),
    license="MIT",
    keywords="ficus framework python",
    url="https://git.sobey.com/SobeyHive/FicusFramework4Py",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Natural Language :: Chinese (Simplified)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    zip_safe=False
)
