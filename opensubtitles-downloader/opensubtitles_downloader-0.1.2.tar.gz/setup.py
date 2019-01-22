from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.2'

install_requires = [
      'send2trash'
]


setup(name='opensubtitles_downloader',
      version=version,
      description="cli program for subtitles download from OpenSubtitles",
      long_description=README + '\n\n' + NEWS,
      classifiers=[
          # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      ],
      keywords='OpenSubtitles, subtitles, downloader',
      author='ubalot',
      author_email='ubalot1@gmail.com',
      url='',
      license='GPLv3',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts':
              ['opensubtitles_downloader=opensubtitles_downloader:main']
      }
)
