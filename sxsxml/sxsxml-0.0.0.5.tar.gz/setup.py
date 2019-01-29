from distutils.core import setup


setup( name = "sxsxml",
       url = "https://bitbucket.org/mjr129/sxsxml",
       version = "0.0.0.5",
       description = "XML stream to stdout with ANSI or HTML formatting",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["sxsxml", "sxsxml.sxs", "sxsxml_tests"],
       install_requires = ["mhelper"],
       python_requires = ">=3.6"
       )
