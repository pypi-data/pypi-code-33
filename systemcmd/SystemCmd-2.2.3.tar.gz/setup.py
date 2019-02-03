import os

from setuptools import setup, find_packages


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename='src/system_cmd/__init__.py')


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ""


setup(name='SystemCmd',
      # python_requires='<3.0',
      author="Andrea Censi",
      author_email="censi@mit.edu",
      url='http://github.com/AndreaCensi/system_cmd',

      description="""My wrappers for subprocess.POpen""",
      long_description=read('README.rst'),
      keywords="",
      license="",

      classifiers=[
          'Development Status :: 4 - Beta',
          # 'Intended Audience :: Developers',
          # 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          # 'Topic :: Software Development :: Quality Assurance',
          # 'Topic :: Software Development :: Documentation',
          # 'Topic :: Software Development :: Testing'
      ],

      version=version,
      download_url='http://github.com/AndreaCensi/system_cmd/tarball/%s' % version,

      entry_points={
          'console_scripts': [
              # 'comptests = comptests:main_comptests'
          ]
      },
      package_dir={'': 'src'},
      packages=find_packages('src'),
      install_requires=[
          'PyContracts',
          'six',
      ],
      tests_require=['nose'],
      )
