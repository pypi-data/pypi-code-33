from setuptools import setup, find_packages
from akoteka.setup.setup import getSetupIni

sp=getSetupIni()

setup(
      name=sp['name'],
      version=sp['version'],
      description='Videoteka',
      long_description="Records your media contents in searchable form",	#=open('README.md', encoding="utf-8").read(),
      url='http://github.com/dallaszkorben/akoteka',
      author='dallaszkorben',
      author_email='dallaszkorben@gmail.com',
      license='MIT',
      classifiers =[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
      ],
      packages = find_packages(),
      setup_requires=[ "pyqt5", "pyqt5-sip", "numpy", "pyttsx3", 'configparser'],
      install_requires=["pyqt5", 'pyqt5-sip', 'numpy','pyttsx3', 'configparser' ],
      entry_points = {
        'console_scripts':
                ['akoteka=akoteka.gui.main_window:main']
      },
      package_data={
        'prala': ['gui/img/*.png'],
        'prala': ['setup/setup.ini'],
        'prala': ['dict/*.properties']
      },
      include_package_data = True,
      zip_safe=False)