import sys, os, os.path, shutil, distutils.util

# Python 3.6 check
if (sys.version_info < (3, 6)):
  raise Exception('Please install Datamode in a Python 3.6+ environment.')


from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages, setup

from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install

# See https://mindtrove.info/4-ways-to-extend-jupyter-notebook/ for a good example on how to install/enable extensions.


# Thanks to https://stackoverflow.com/questions/17887905/python-setup-py-to-run-shell-script
class install(_install):
  def run(self):
    _install.run(self)


class develop(_develop):
  def run(self):
    # Hack to prevent data_files from executing in dev mode.
    self.distribution.data_files = []

    _develop.run(self)
    # Install the extension features_react into Jupyter Notebook
    install_jupyter_react_bridge()

    # Copy sample file to working copy
    if not os.path.exists('dev.py'):
      print ('Copied docs/dev/dev.py.sample to dev.py - edit to run your own transforms')
      shutil.copyfile('docs/dev/dev.py.sample', 'dev.py')


def install_jupyter_react_bridge():
  from notebook.nbextensions import install_nbextension

  symlink_dir = os.path.join(os.path.dirname(__file__), "js", "staticdev")
  full_dest = install_nbextension(symlink_dir, symlink=True,
                      overwrite=True, prefix=sys.prefix, user=False, destination="features_react")

  print ('Symlinked extension source={symlink_dir} to dest={full_dest}'.format(full_dest=full_dest, symlink_dir=symlink_dir))
  enable_extension_in_notebook(full_dest, symlink_dir)


def enable_extension_in_notebook(full_dest, symlink_dir):
  from notebook.services.config import ConfigManager

  cm = ConfigManager()
  cm.update('notebook', {"load_extensions": {"features_react/index": True } })
  print ('Enabled Jupyter notebook extension in {full_dest} (setup_mode=develop, symlink_dir={symlink_dir}).'.format(full_dest=full_dest, symlink_dir=symlink_dir))


# Use Readme as the long_description for PyPI
with open('readme.md') as f:
  long_description = f.read()


# https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
# https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Distributing%20Jupyter%20Extensions%20as%20Python%20Packages.html
setup(
  name='datamode',
  cmdclass={
    'develop': develop,
    'install': install,
  },
  version='0.0.9',
  license='Apache 2.0',
  project_urls={
    'Main website': 'https://www.datamode.com',
    'Documentation': 'https://datamode.readthedocs.io/',
    'Source': 'https://github.com/datamode/datamode/',
    'Tracker': 'https://github.com/datamode/datamode/issues',
  },
  url='https://www.datamode.com',
  author='Vaughn Koch',
  author_email='code@datamode.com',
  description="A tool to quickly build data science pipelines",
  long_description=long_description,
  long_description_content_type='text/markdown',
  package_dir={'': 'src'},
  packages=find_packages('src'),
  py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
  include_package_data=True,  # Include everything in src/
  data_files=[
    # like `jupyter nbextension install --sys-prefix`
    ('share/jupyter/nbextensions/features_react', [
        'src/datamode/dist/index.js',
    ]),
    # like `jupyter nbextension enable --sys-prefix`
    ('etc/jupyter/nbconfig/notebook.d', [
        'src/datamode/jupyter-config/nbconfig/notebook.d/datamode.json'
    ]),
  ],

  zip_safe=False,

  setup_requires=[
    'jupyter >= 1.0.0',
  ],

  install_requires=[
    ### Utilities
    'Pygments >= 2.3.1',
    'colorama >= 0.4.1',
    'pytz >= 2018.9',
    'python-dateutil >= 2.7.5',

    ### Data manipulation
    'pyparsing >= 2.3.1',

    ### Datastores
    'SQLAlchemy >= 1.2.16',
    'mysql-connector-python >= 8.0.14',
    'psycopg2-binary >= 2.7.6.1',  # Preferred version now instead of 'psycopg2'
    'boto3 >= 1.9.83',

    ### Machine learning related
    'numpy >= 1.16.0',
    'scipy >= 1.2.0',
    'pandas >= 0.23.4',
    'scikit-learn >= 0.20.2',


    ### NLP
    'gensim >= 3.6.0',
    # 'python-Levenshtein >= 0.12.0',

    # This is the official fastText python library - they haven't released to PyPI yet.
    # To date, the python FT wrappers on PyPI are 3rd party libraries.
    # 'fastText >= 0.8.22',

    ### Dataviz
    'altair >= 2.3.0',
    'statsmodels >= 0.9.0',
    'seaborn >= 0.9.0',

    ###
    ### Notebook
    ###
    'jupyter >= 1.0.0',
    'jupyter-contrib-nbextensions >= 0.5.1',

    ### Core data handling
    'pyarrow >= 0.12.0',

    ### Jupyter-React
    'jupyter-react >= 0.1.3',

    ### Analytics
    'analytics-python >= 1.2.9',
  ],


  # dependency_links=[
  #   'git+https://github.com/facebookresearch/fastText.git@v0.2.0#egg=fastText-0.8.22',
  # ],

  keywords=[
    'datamode',
    'dataviz',
    'data science',
    'data transformation',
    'feature engineering',
    'data prep',
    'data preparation',
    'data munging',
    'data visualization',
  ],

  classifiers=[
      "Development Status :: 4 - Beta",
      'Programming Language :: Python',
      'Programming Language :: Python :: 3 :: Only',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      "Topic :: Utilities",
      "Topic :: Software Development :: User Interfaces",
      "Topic :: Scientific/Engineering :: Visualization",
      "Topic :: Scientific/Engineering :: Artificial Intelligence",
      "Operating System :: OS Independent",
      "License :: OSI Approved :: Apache Software License",
  ]
)
