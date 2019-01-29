from distutils.core import setup

def __rld():
    try:
        import os.path
        with open(os.path.join(os.path.dirname(__file__), "readme.rst")) as file:
            return file.read()
    except Exception as ex:
        return "(could not load readme: {})".format(ex)

setup( name = "editorium",
       url = "https://bitbucket.org/mjr129/editorium",
       version = "0.0.0.30",
       description = "Creates a Qt Editor for arbitrary Python Objects using Reflection.",
       long_description = __rld(),
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["editorium",
                   "editorium.controls",
                   "editorium_test"],
       python_requires = ">=3.6",
       install_requires = ["py-flags",
                           "sip",
                           "PyQt5",
                           "mhelper",
                           "stringcoercion"],
       )
