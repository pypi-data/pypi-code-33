import os
import subprocess
import shutil

from setuptools import setup, findall, Command
from setuptools.command.sdist import sdist as Sdist


version = '0.3.2'


def listStatic():
  return (os.path.relpath(p, 'chronologerui') for p in findall('chronologerui/static'))

# The initial value is needed for ``static`` to be installed.
# Re-populated in QxBuildCommand on build where it's initially empty.
staticFiles = list(listStatic())


class QxBuildCommand(Command):

  description = 'build the frontend Qooxdoo application'


  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    output = subprocess.check_output('python --version', shell = True, stderr = subprocess.STDOUT)
    assert output.decode().startswith('Python 2.7'), 'Qooxdoo SDK requires Python 2'
    assert os.path.exists('generate.py'), 'No Qooxdoo generator script found'

    shutil.rmtree('chronologerui/static', ignore_errors = True)

    if not os.path.exists('library'):
      subprocess.run('python generate.py -m VERSION:{} load-library'.format(version), shell = True)

    subprocess.run('python generate.py -m VERSION:{} build'.format(version), shell = True)
    shutil.move('build', 'chronologerui/static')

    # Needed for 1st build with a new set of files.
    staticFiles.extend(listStatic())


class CustomSdist(Sdist):

  def run(self):
    self.run_command('build_qx')
    super().run()


setup(
  name             = 'ChronologerUI',
  version          = version,
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  license          = 'GPL-3.0',
  url              = 'https://bitbucket.org/saaj/chronologer/src/frontend',
  description      = 'Graphical user interface for the Python HTTP logging server',
  long_description = open('README.rst').read(),
  platforms        = ['Any'],
  packages         = ['chronologerui'],
  package_data     = {'chronologerui': staticFiles},
  classifiers      = [
    'Framework :: CherryPy',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: Implementation :: CPython',
    'Intended Audience :: Developers'
  ],
  install_requires = ['cherrypy < 9'],
  cmdclass         = {
    'build_qx' : QxBuildCommand,
    'sdist'    : CustomSdist
  },
)

