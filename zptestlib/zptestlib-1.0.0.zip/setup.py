# from distutils.core import setup
from setuptools import setup

def readme_file():
      with open("README.rst", encoding="utf-8") as rf:
            return rf.read()

setup(name = "zptestlib", version = "1.0.0", description = "this is a niu bi lib",
      packages = ["zptestlib"], py_modules = ["Tool"], author = "zp", author_email = "610586533@qq.com",
      long_descripyion = readme_file(),
      url = "https://github.com/zoupeng/Python_code", license = "MIT")