"""
Intermake setup.
"""
from distutils.core import setup


def __rld():
    try:
        import os.path
        with open( os.path.join( os.path.dirname( __file__ ), "readme.rst" ) ) as file:
            return file.read()
    except Exception as ex:
        return "(could not load readme: {})".format( ex )


setup( name = "intermake",
       version = "1.0.0.78",
       description = "Automated run-time generation of user interfaces from Python functions - command-line-args, CLI, python-interactive, python-scripted, graphical (Qt GUI)",
       long_description = __rld(),
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       url = "https://bitbucket.org/mjr129/intermake",
       python_requires = ">=3.6",
       
       entry_points = \
           {
               "console_scripts": ["intermake = intermake.__main__:main"]
           },
       
       packages = \
           [
               "intermake",
               "intermake.commands",
               "intermake.engine",
               "intermake.extensions",
               "intermake.framework",
               "intermake.helpers",
               "intermake_qt",
               "intermake_qt.extensions",
               "intermake_qt.forms",
               "intermake_qt.forms.designer",
               "intermake_qt.forms.designer.resource_files",
               "intermake_qt.utilities",
               "intermake_test",
               "intermake_debug"
           ],
       
       install_requires = \
           [
               "colorama",
               "stringcoercion",
               "editorium",
               "py-flags",
               "mhelper",
               "sxsxml",
               "docutils",
               "PyQt5"
           ],

       classifiers = \
           [
               "Development Status :: 3 - Alpha",
        
               "Environment :: Console",
               "Environment :: Win32 (MS Windows)",
               "Environment :: X11 Applications :: Qt",
               "Environment :: MacOS X",
               "Operating System :: OS Independent",
               "Operating System :: Microsoft :: Windows",
               "Operating System :: MacOS",
               "Operating System :: POSIX :: Linux",
        
               "Intended Audience :: Developers",
               "Topic :: Utilities",
               "Topic :: Terminals",
               "Topic :: Multimedia :: Graphics :: Presentation",
        
               "License :: OSI Approved :: GNU Affero General Public License v3",
               "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        
               "Natural Language :: English",
               "Programming Language :: Python :: 3.6",
               "Programming Language :: Python :: 3",
               "Programming Language :: Python :: 3 :: Only",
               "Programming Language :: Other Scripting Engines"
           ]
       )
