import re, numpy

from setuptools import find_packages, setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

packages = find_packages(exclude=["tests*"])

version = re.search('^__version__\s*=\s*"(.*)"', open("cognite_ml/__init__.py").read(), re.M).group(1)
cmdclass = { }
ext_modules = [ ]

ext_modules += [Extension("cognite_ml.filters.perona_malik", 
                         [ "cognite_ml/filters/perona_malik.pyx" ],
                         cython_directives={"c_string_type": "str", "c_string_encoding": "utf8"},
                         language='c++',)]
cmdclass.update({ 'build_ext': build_ext })

setup(
    name="cognite-ml",
    version=version,
    description="Cognite Machine Learning Toolkit",
    url="https://github.com/cognitedata/cognite_ml",
    download_url="https://github.com/cognitedata/cognite_ml/archive/{}.tar.gz".format(version),
    author="Data Science Cognite",
    author_email="que.tran@cognite.com",
    packages=packages,
    install_requires=[],
    include_package_data=True,
    ext_modules = ext_modules,
    include_dirs=[numpy.get_include()],
    cmdclass = cmdclass
)
