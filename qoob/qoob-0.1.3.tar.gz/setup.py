#!/usr/bin/python3
import os
import setuptools
import setuptools.command.build_py
here = os.path.abspath(os.path.dirname(__file__))


class CreateDesktopFile(setuptools.command.build_py.build_py):
  def run(self):
    with open(os.path.join(here + "/qoob.desktop"), 'w') as f:
        f.write("[Desktop Entry]\n")
        f.write("Name=qoob\n")
        f.write("GenericName=Music Player\n")
        f.write("Terminal=false\n")
        f.write("Type=Application\n")
        f.write("Categories=Utility;\n")
        f.write("Icon=qoob\n")
        f.write("Exec=qoob\n")
    setuptools.command.build_py.build_py.run(self)


# Workaround in case PyQt5 was installed without pip
install_requires=['mutagen']
try:
    # Compile ui files to python
    from PyQt5 import uic
    uic.compileUiDir('qoob/ui')
except:
    install_requires.append("pyqt5")

setuptools.setup(
    name='qoob',
    version='0.1.3',
    description='foobar-like music player for Linux',
    keywords='music folder player audio media linux',
    author='William Belanger',
    url='https://gitlab.com/william.belanger/qoob',

    # From https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass={'build_py': CreateDesktopFile},
    data_files=[
        ('share/icons/hicolor/scalable/apps', ['qoob/icons/qoob.svg']),
        ('share/applications', ['qoob.desktop'])
    ],
    package_data={'': ['icons/*', 'icons/dark/*.svg', 'icons/light/*.svg']},
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'qoob=qoob:main',
        ],
    },
)
